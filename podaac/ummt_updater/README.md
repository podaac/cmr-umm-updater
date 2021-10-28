# ummt_updater
These files are used for updating the CMR UMM-T profile.
Developer should update the UMM-T tool json file in the service cmr directory with any significant changes to the service features.

python ummt_updater.py -f netcdf_cmr_umm_t.json -n mmt_service_4479 -c S1234779679-POCLOUD -p POCLOUD
See usage information by running ummt_updater.py -h

## Errors

If you get the error:

`socket.gaierror: [Errno 8] nodename nor servname provided, or not known`

then you are *probably* running on a mac. You'll need to add '127.0.0.1 MACHINE_NAME' to your /etc/hosts file in order for this to work. MACHINE_NAME 
can be found by running `echo $HOSTNAME` on the command line.

Thanks to StackOverflow for figuring that out:
https://apple.stackexchange.com/questions/253817/cannot-ping-my-local-machine
