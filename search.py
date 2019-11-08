#!/usr/bin/python3
"""
    script for searching events using 

    curl -X GET --header 'Accept: application/json' 'https://10.35.36.165/api/internal/event?event_type=Audit'

    then

    curl -X GET --header 'Accept: application/json' 
    'https://10.35.36.165/api/internal/event?after_id=2019-10-31%3A11%3A3%3A%3A%3A1572521711478-266a63ee-91cc-49e4-ba5f-04b40f4f1f44&event_type=Audit'


"""
from urllib.parse import quote
import json, os

try:
    with open('auth.cfg', 'r') as auth:
        auth_path = auth.readline().rstrip()
except:
    auth_path = None
    pass
auth = '-H "Authorization: Basic $(cat %s | base64)"'%(auth_path) if auth_path is not None else None

def get_curl_response(curl):
    #print(curl)
    os.system('%s | python -m json.tool > response.json'%(curl))
    with open('response.json', 'r') as f:
        response = json.load(f)
        #log("Response: %s"%(response), kw)
        return response


def parse_args(args):
    """
        parses:
            -n 192.168.1.10
            --node_ip 192.168.1.10
        Returns:
        {'-n': '192.168.1.10'} or {'--node_ip': '192.168.1.10'}
    """
    argDict = {}
    for index, arg in enumerate(args):
        if '--' in arg:
            if len(args) >= index+1:
                argDict[arg] = args[index+1]
            else:
                usage(f'missing argment for {arg}')
                return
    return argDict

def find_all_events(args):
    header = "--header 'Accept: application/json'"
    query = ''
    queryOptions = {
        '--event_type':[
            "Archive","Audit","AuthDomain",
            "Backup","CloudNativeSource","Configuration",
            "Diagnostic","Discovery","Instantiate",
            "Maintenance","NutanixCluster"
            ], 
        '--status': [
            'Failure', 'Warning', 'Running', 
            'Success', 'Canceled', 'Canceling'
            ], 
        '--object_type': [
            'VmwareVm', 'Mssql', 'LinuxFileset', 'WindowsFileset', 
            'WindowsHost', 'LinuxHost', 'StorageArrayVolumeGroup', 
            'VolumeGroup', 'NutanixVm', 'Oracle', 'AwsAccount',
            'Ec2Instance'
            ], 
        '--object_ids': [],
        '--object_name': []
    }
    for option in queryOptions:
        if option in args:
            if len(queryOptions[option]) > 0:
                if args[option] in queryOptions[option]:
                    query = query + f'{option[2:]}={args[option]}&'
                else:
                    usage(f"Incorrect usage of {option} available options\n{queryOptions[option]}")
                    return
            else:
                query = query + f'{option[2:]}={quote(args[option])}&'


    print(query)
    url = f"'https://{args['--node_ip']}/api/internal/event?{query[:-1]}'"
    print(url)
    resultChecker=0
    while True:
        curl = "curl -s -X GET %s %s %s --insecure"%(auth, header, url)
        results = get_curl_response(curl)
        for data in results["data"]:
            #print(data["eventInfo"])
            if "message" in data["eventInfo"]:
                message = data["eventInfo"][:data["eventInfo"].index(',"id":')].split('{')[1][10:]
                #print(message)
                if args['--search_string'] in message:
                    if not args['--output'] == 'console':
                        #toWrite = {"eventInfo": data["eventInfo"][:1000], "date": data["id"]}
                        with open(args['--output'], 'a') as r:
                            r.write(data["id"]+'\n'+str(data["eventInfo"][:1000])+'\n\n')
                    else:
                        print(data["id"]+'\n'+str(data["eventInfo"][:1000])+'\n\n')

        if results["hasMore"] == False:
            print("\n\nLast date in events search, no older events exist in events_table: \n")
            print(results["data"][-1]["id"])
            break
        resultChecker+=1
        safeId = quote(results["data"][-1]["id"])
        url = f"'https://{args['--node_ip']}/api/internal/event?after_id={safeId}&{query}'"

        if resultChecker > 10:
            print("\n\nCurrent date in events search: \n")
            print(results["data"][-1]["id"])
            resultChecker=0
def usage_help():
    usage("Manual for event searcher\n")
    print("""
--status: 
    'Failure', 'Warning', 'Running', 'Success', 
    'Canceled', 'Canceling’
--event_type: 
    "Archive","Audit","AuthDomain",
    "Backup","CloudNativeSource","Configuration",
    "Diagnostic","Discovery","Instantiate",
    "Maintenance","NutanixCluster","Recovery",
    "Replication","StorageArray","StormResource",
    "System","Vcd","VCenter"

--object_ids:
    Filter by a comma separated list of object IDs. 
    Should only specify at most one of object_name and object_ids.
    Example:
        "Fileset:::02d72804-7cc1-4e40-a465-95a5d868f0e9,VirtualMachine:::94f70c11-0775-4562-b9a8-9d19dd4fca56-vm-79879"
        ./search.py --node_ip 10.35.36.165 
            --object_ids "Fileset:::02d72804-7cc1-4e40-a465-95a5d868f0e9,VirtualMachine:::94f70c11-0775-4562-b9a8-9d19dd4fca56-vm-79879" 
            --status Failure  --search_string 'Could not fetch snapshot disk data'

--object_name:
    Example:
        ./search.py --node_ip 10.35.36.165 --object_name data2 --status Failure  --search_string 'Internal server error'

--object_type:
    Filter all the events by object type. Enter any of the following values:
        'VmwareVm', 'Mssql', 'LinuxFileset', 'WindowsFileset', 'WindowsHost', 'LinuxHost',
        'StorageArrayVolumeGroup', 'VolumeGroup', 'NutanixVm', 'Oracle', 'AwsAccount',
        and 'Ec2Instance'. WindowsHost maps to both WindowsFileset and VolumeGroup, 
        while LinuxHost maps to LinuxFileset and StorageArrayVolumeGroup.
    """)

def usage(message=None):
    if message is not None:
        print(message)
    print("""
Usage: 
    ./search.py --node_ip <ip> [options] --search_string <searchForMessage>

    ./search.py <--node_ip XX.XX.XX.XX > [--event_type <type>] [--status <type>][--event_type <type>] 
                [--object_ids "VirtualMachine:::<id>,FileSet:::<id>"] [--object_name <name>] [--object_type <objtype>]
                [--output <console (default) | file-name.log ][--help] < --search_string messagestring >
Example:
    ./search.py --node_ip 10.35.36.165 ----event_type Audit --output results.log --search_string 'created local user'
    """)

def main():
    import sys
    args = sys.argv
    if '--help' in args:
        usage_help()
        return
    args=parse_args(args[0:])
    print(args)
    
    if not '--search_string' in args:
        usage("missing --search_string <message> ")
        return
    if not '--output' in args:
        args['--output'] = 'console'
    find_all_events(args)

if __name__ == '__main__':
    main()