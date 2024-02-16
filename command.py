import os

puppet_ids = os.listdir("./arguments")
commands = [f"python3 sockpuppet.py './arguments/puppets/{puppet_id}'\n" for puppet_id in puppet_ids]

f = open("startup-commands.txt", "w")
f.writelines(commands)
f.close()


