# Rubrik-search-events
A command-line utility to search all event messages with Rubrik CDM based on a particular string. 

# Get Started

    $ git clone https://github.com/codemation/Rubrik-search-events.git

### 1 - Create an credentials file:
Credential file should contain username password in the following  format 'username:pw'

    $ echo -n 'admin:abcd1234' > ~/special_cdm_auth

### 2 - Update auth.cfg 
Within search-events folder with credential file location. 

    $ echo -n '~/special_cdm_auth' > auth.cfg

## Usage:

    ./search.py --node_ip <ip> [options] --search_string <searchForMessage>

    ./search.py <--node_ip XX.XX.XX.XX > [--event_type <type>] [--status <type>][--event_type <type>] 
                [--object_ids "VirtualMachine:::<id>,FileSet:::<id>"] [--object_name <name>] [--object_type <objtype>]
                [--output <console (default) | file-name.log ][--help] < --search_string messagestring >

## Example:

    ./search.py --node_ip 10.35.36.165 ----event_type Audit --output results.log --search_string 'created local user'

    ./search.py --node_ip 10.35.36.165 --object_name data2 --status Failure  --search_string 'Internal server error'

    ./search.py --node_ip 10.35.36.165 --object_ids "Fileset:::02d72804-7cc1-4e40-a465-95a5d868f0e9,VirtualMachine:::94f70c11-0775-4562-b9a8-9d19dd4fca56-vm-79879" --status Failure  --search_string 'Could not fetch snapshot disk data'

    ./search.py --node_ip 10.35.36.165 --object_name data2 --object_type LinuxFileset --status Failure  --search_string '' --output all_failures_data2_fileset.log

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