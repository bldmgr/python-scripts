import requests
from requests.auth import HTTPDigestAuth
import sys
import os
import hashlib
import argparse

download_dict = {}
download_dict['file_name']='group'
download_dict['file_name']='group'
download_dict['file_name']='group'
download_dict['file_name']='group'

def main(argv):
    parser = argparse.ArgumentParser(
        description="Nexus file download script"
    )

    parser.add_argument(
        '-u', '-username',
        dest='username',
        help="Specifies the username to connect to Nexus with",
        default="",
        required=True)

    parser.add_argument(
        '-p', '-password',
        dest='password',
        help="",
        default="",
        required=True)

    args = parser.parse_args()

    start_search(args.username, args.password)

def start_search(username, password):
    for download_item in download_dict.items():
        continuation_token = '1st'
        group = download_item[1]
        version = download_item[0]
        while continuation_token is not None:
            page = pagination_nexus(username, password, 'raw', group, continuation_token)
            for d in page:
                if d == 'items':
                    for items in page[d]:
                        if version in items['path']:
                            nexus_md5 = items['checksum']
                            download_file = download_nexus(items['downloadUrl'])
                            calculated_md5 = check_download(download_file)
                            for i in nexus_md5:
                                if i == 'md5':
                                    if calculated_md5 == nexus_md5[i]:
                                        print('Verify Downloaded File : {} to {}'.format(calculated_md5, nexus_md5[i]))

                if d == 'continuationToken':
                    continuation_token = page[d]


def pagination_nexus(username, password, repository, group, continuation_token):
    endpoint = 'repository=%s&group=%s' %(repository, group)
    if continuation_token == '1st':
        url = 'https://localhost/service/rest/v1/search/assets?%s' %(endpoint)
    else:
        url = 'https://localhost/service/rest/v1/search/assets?%s&continuationToken=%s' %(endpoint, continuation_token)

    r = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password))

    return r.json()


def download_nexus(url):
    download_filename = url.split('/')[-1]
    print('Downloading... : {}'.format(download_filename))
    if os.path.exists(download_filename):
        os.remove(download_filename)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(download_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return download_filename

def check_download(file_name):
    with open(file_name, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return file_hash.hexdigest()

if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as error:
        print("Aborting...")
        print("{}".format(error))
        sys.exit(1)

