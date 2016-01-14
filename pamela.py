#######################
## PAMELA par decomb_s
#######################

import os, syslog, sys

list_users = {}
global current_login
global current_key

def manage_login():
    try:
        fileis = open("/lib/security/account", 'r')
    except:
        sys.stderr.write("Error, cannot open account file\n");
        sys.exit(-1)
    text_in_file = fileis.read()
    fileis.close()
    list_file = text_in_file.split('\n')
    i = 1
    while i < len(list_file):
        list_tmp = list_file[i].split(':')
        list_users[list_tmp[0]] = list_tmp[1]
        i += 1

def check_auth(user, pwrd):
    global current_login

    manage_login()
    for i in list_users:
        if i == user:
            if pwrd == list_users[i]:
                current_login = i
                print current_login
                return True
    return False

def init_container():
    if os.path.isdir("/home/containers") == False:
        os.system("mkdir /home/containers")
    if os.path.exists("/home/containers/" + current_login + ".img") == False:
        print "Creating Container..."
        cmd = "dd if=/dev/urandom of=/home/containers/"
        cmd += current_login
        cmd += ".img bs=1024 count=0 seek=614400"
        os.system(cmd)
        return False
    return True


def loop_container():
    print "Loop container..."
    cmd = "losetup /dev/loop0 /home/containers/"
    cmd += current_login
    cmd += ".img" 
    os.system(cmd)

def generate_key():
    global current_key

    if os.path.isdir("/home/containers/.keys") == False:
        os.system("mkdir /home/containers/.keys")
    if os.path.exists("/home/containers/.keys/" + current_login + ".key") == False:
        print "Generate keyfile..."
        cmd = "dd if=/dev/urandom of=/home/containers/.keys/"
        cmd += current_login
        cmd +=".key bs=1024 count=4"
        os.system(cmd)
    current_key = "/home/containers/.keys/"
    current_key += current_login
    current_key += ".key"
    os.system("chmod 0400 " + current_key)

def format_device():
    print "Encrypting of the container ..."
    vname = current_login + "_tmp"
    os.system("sudo cryptsetup luksFormat /dev/loop0 " + current_key)
    os.system("sudo cryptsetup luksOpen -d " + current_key + " /dev/loop0 " + vname)
    os.system("sudo mkfs.vfat -F 32 /dev/mapper/" + vname)

def mount_container():
    print "Mounting container ..."
    if os.path.isdir("/home/" + current_login + "/my_encrypted_place") == False:
        os.system("mkdir /home/" + current_login + "/my_encrypted_place")
        os.system("chmod 777 /home/" + current_login + "/my_encrypted_place")
    os.system("mount -t vfat -o umask=000 /dev/mapper/" + current_login + "_tmp /home/" + current_login + "/my_encrypted_place")
    os.system("sudo chgrp partitons -R /home/" + curren_login + "/my_encrypted_place")
    os.system("sudo chmod +grwxs -R /home/" + current_user + "/my_encrypted_place")

def umount_container():
    syslog.syslog(syslog.LOG_AUTH, "Unmounting container...")
    os.system("umount /home/" + current_login + "/my_encrypted_place")

def close_container():
    syslog.syslog(syslog.LOG_AUTH, "Closing container")
    os.system("cryptsetup luksClose " + current_login + "_tmp")

def open_container():
    print "Opening container..."
    loop_container()
    generate_key()
    os.system("cryptsetup luksOpen /dev/loop0 " + current_login + "_tmp -d " + current_key)

def clean_loop():
    syslog.syslog(syslog.LOG_AUTH, "Closing /dev/loop0")
    os.system("sudo losetup -d /dev/loop0")

def manage_containers():
    if init_container() == False:
        loop_container()
        generate_key()
        format_device()
        mount_container()
    elif init_container() == True:
        open_container()
        mount_container()

def pam_sm_authenticate(pamh, flags, argv):
    pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "PAMELA Authentification ..."))
    if pamh.user == "root":
        return pamh.PAM_SUCCESS
    pwrd = pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "Password to unlock your container: ")).resp
    if pwrd == "":
        pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Wrong password"))
        return pamh.PAM_AUTH_ERR
    if check_auth(pamh.user, pwrd) == False:
        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Authentification ERROR"))
        return (pamh.PAM_AUTH_ERR)
    pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Authentification success."))
    pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Initialisation begin ...be patient..."))
    manage_containers()
    return pamh.PAM_SUCCESS

def pam_sm_end(pamh):
    syslog.syslog(syslog.LOG_AUTH, "Closing Pamela Ressources...")
    umount_container()
    close_container()
    clean_loop()
    return pamh.PAM_SUCCESS

def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
    return pamh.PAM_SUCCESS


def main():
    check_auth("test", "test")

if __name__ == "__main__":
    main()
