import paramiko
import stat
from pathlib import Path
from zipfile import ZipFile
import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',           help='SFTP server address', required=True)
    parser.add_argument('--port',           help='SFTP server port', required=True)
    parser.add_argument('--username',       help='SFTP server username', required=True)
    parser.add_argument('--password',       help='SFTP server password', required=True)
    parser.add_argument('--remotedir',      help='SFTP directory to copy from', required=True)
    parser.add_argument('--localdir',       help='Local directory to copy to', required=True)
    parser.add_argument('--filepasswords',  help='text file containing decryption passwords '
                                                 'and their associated file names', required=True)
    args = parser.parse_args()

    transport = paramiko.Transport((args.host, int(args.port)))
    transport.connect(None, args.username, args.password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    files = get_dir(sftp, args.remotedir)
    downloaded_files = download(sftp, args.localdir, files)
    unzip(downloaded_files, get_password_map(args.filepasswords))


def get_password_map(pw_file):
    """
    Creates a map with filename keys and password values used to decrypt zip files
    """
    zip_passwords = {
    }
    try:
        f = open(pw_file)
        for line in f:
            pair = line.split(" ")
            if len(pair) > 1:
                zip_passwords[pair[0]] = pair[1].strip('\n')
    except:
        e = sys.exc_info()[0]
        print("unable to open file {} - {}".format(pw_file, e))


    return zip_passwords


def get_dir(sftp, current_dir):
    """
    Flattens all files in the specified directory tree into a list of file paths
    """
    ftp_dir = sftp.listdir_attr(current_dir)
    files = []
    for i in ftp_dir:
        if stat.S_ISDIR(i.st_mode):
            for j in get_dir(sftp, "{}/{}".format(current_dir, i.filename)):
                files.append(j)
        else:
            files.append("{}/{}".format(current_dir, i.filename))
    return files


def download(sftp, home_root_directory, files):
    """
    Downloads all non duplicate files at the specified ftp location
    """
    downloaded_files = []
    for i in files:
        # Fill in missing directories
        path = Path("{}/{}".format(home_root_directory, '/'.join(i.split('/')[0:-1])))
        path.mkdir(parents=True, exist_ok=True)
        # Skip if file exists
        local_path = Path("{}/{}".format(home_root_directory, i))
        if not local_path.exists():
            try:
                print("getting {}...".format(i))
                sftp.get(i, "{}/{}".format(home_root_directory, i[2:]))
            except:
                e = sys.exc_info()[0]
                print("an error occurred while transferring {} - {}".format(i, e))
                # Delete the partially downloaded file
                if local_path.exists():
                    local_path.unlink()
            else:
                downloaded_files.append(local_path)
        else:
            print("skipping {}".format(i))
            downloaded_files.append(local_path)
    return downloaded_files


def unzip(downloaded_files, zip_passwords):
    """
    Unzips all specified file paths to a directory adjacent to the zipped file with the same name
    """
    for i in downloaded_files:
        with ZipFile(i) as zip_file:
            key = i.name.split('.')[0].split('_')[-1]
            if key in zip_passwords:
                try:
                    new_path = '/'.join(i.parts).split('.')[0]
                    Path(new_path).mkdir(parents=True, exist_ok=True)
                    zip_file.extractall(path=new_path, pwd=bytes(zip_passwords[key], encoding='utf8'))
                except:
                    e = sys.exc_info()[0]
                    print("unable to extract {} - {}".format(i, e))


if __name__ == '__main__':
    main()
