from argparse import ArgumentParser
from random import choice
import docker
from time import sleep
import os
import pandas as pd
from uuid import uuid4
import json

# change this to your own ID
IMAGE_NAME = 'ss/youtube-sock-puppet'
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
ARGS_DIR = os.path.join(os.getcwd(), 'arguments')
#NUM_TRAINING_VIDEOS = 5
WATCH_DURATION = 30
USERNAME = os.getuid()

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--build', action="store_true", help='Build docker image')
    parser.add_argument('--run', action="store_true", help='Run all docker containers')
    parser.add_argument('--simulate', action="store_true", help='Only generate arguments but do not start containers')
    parser.add_argument('--max-containers', default=10, type=int, help="Maximum number of concurrent containers")
    parser.add_argument('--sleep-duration', default=60, type=int, help="Time to sleep (in seconds) when max containers are reached and before spawning additional containers")
    parser.add_argument('--start', default=1, type=int, help="Start Index of sock puppets to spawn")
    parser.add_argument('--end', default=10, type=int, help="End Index of sock puppets to spawn")
    parser.add_argument('--videos', default='data/videos_sh.csv', help='Path to the videos file')
    parser.add_argument('--testing-videos', default='data/videos_sh.csv', help='Path to the testing videos file')
    args = parser.parse_args()
    return args, parser

def build_image():
    # get docker client and build image
    client = docker.from_env()

    # build the image from the Dockerfile
    #   -> tag specifies the name
    #   -> rm specifies that delete intermediate images after build is completed
    _, stdout = client.images.build(path='.', tag=IMAGE_NAME, rm=True)
    for line in stdout:
        if 'stream' in line:
            print(line['stream'], end='')
    
def get_mount_volumes():
    # binds "/output" on the container -> "OUTPUT_DIR" actual folder on disk
    # binds "/args" on the container -> "ARGS_DIR" actual folder on disk
    return { OUTPUT_DIR: { "bind": "/output" }, ARGS_DIR: { "bind": "/args" } }

def max_containers_reached(client, max_containers):
    try:
        return len(client.containers.list()) >= max_containers
    except:
        return True
    
def in_range(df, low, high):
    return df.iloc[low:high]


def get_videos(videos_file, user_id):
    # read the videos file
    videos = pd.read_csv(videos_file)[user_id].to_list()
    # return the videos
    return videos

def spawn_containers(args):
    # get docker client
    client = docker.from_env()

    USERS = [f'user_{i}' for i in range(args.start, args.end + 1)]
    
    # spawn containers for each user
    count = 0

    # create required directories
    if not os.path.exists(ARGS_DIR):
        os.makedirs(ARGS_DIR)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for user in USERS:
        # check for running container list
        while max_containers_reached(client, args.max_containers):
            # sleep for a minute if maxContainers are active
            print("Max containers reached. Sleeping...")
            sleep(args.sleep_duration)
        # read videos for intervention
        videos = get_videos(args.videos, user_id=user)
        # get seeds
        seeds = videos #pd.read_csv(args.testing_videos)['video_id'].to_list()

        # try test seeds
        testSeed = choice(seeds)

        # generate a unique puppet identifier
        puppetId = f'{user},{testSeed},{str(uuid4())[:8]}'

        # write arguments to a file
        with open(os.path.join(ARGS_DIR, f'{puppetId}.json'), 'w') as f:
            puppetArgs = dict(
                puppetId=puppetId,
                # duration to watch each video
                duration=WATCH_DURATION,
                # a description
                description='',
                # output directory for sock puppet
                outputDir='/output',
                # videos to watch
                intervention=videos,
                # seed video
                testSeed=testSeed,
                # steps to perform
                steps='trainWatch,test'
            )
            json.dump(puppetArgs, f, indent=4)


        # spawn container if it's not a simulation
        if not args.simulate:
            print("Spawning container...")
            # set outputDir as "/output"
            command = ['python3', 'sockpuppet.py', f'/args/{puppetId}.json']

            # run the container
            client.containers.run(IMAGE_NAME, command, volumes=get_mount_volumes(), shm_size='512M', remove=True, user=USERNAME, detach=True)
            # Capture and print the logs
            #logfile = []
            #logs = container.logs(stdout=True, stderr=True, stream=True)
            #for log in logs:
            #  print(log.decode('utf-8').strip())
            #  logfile.append(log.decode('utf-8').strip())

            # Optionally, you can wait for the container to finish and get the exit code
            #exit_code = container.wait()['StatusCode']
            #logfile.append(f"Container exited with code: {exit_code}")
            #print(f"Container exited with code: {exit_code}")
            #f = open(f"output/logfile_{puppetId}.txt", "w")
            #f.writelines(logfile)
            #f.close()
        # increment count of containers
        count += 1
 
    print("Total containers spawned:", count)

def main():

    args, parser = parse_args()

    if args.build:
        print("Starting docker build...")
        build_image()
        print("Build complete!")

    if args.run:
        print("Starting docker containers...")
        spawn_containers(args)

    if not args.build and not args.run:
        parser.print_help()


if __name__ == '__main__':
    main()
