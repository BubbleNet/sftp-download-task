# sftp-download-task

sftp-download-task is a script used to connect to a sftp server, download a directory, and decrypt the downloaded files.

### Dependencies

Only one nonstandard dependency is required.

```text
pip install paramiko
```

### Usage

the following arguments are required to run this script

`--host` SFTP server address

`--port` SFTP server port

`--username` SFTP server username

`--password` SFTP server password

`--remotedir` SFTP directory to copy from

`--localdir` Local directory to copy to

`-filepasswords` text file containing decryption passwords and their associated file names

The following example shows how to run the script

```
> python3 sftp.download-task.py --host="sftp.example.com" --port=22 
--username="my-user" --password="my-password" --remotedir="." 
--localdir="./data" --filepasswords="./test-passwords.txt"
```

### Behavior

The sftp-download-task script will not download files that already exist on the local machine.

The last portion of the filename must match the identifier in the provided filepasswords file. for example `ev_data_123456.zip` be matched with the identifier `123456` from the password file.

The filepasswords file must only include identifier-password pairs separated by a space. Each pair must be separated by a newline.

The following is an example of a filepasswords file

```text
123456 password1
23456789 password2
3458 pw3
```