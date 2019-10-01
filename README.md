All you _should_ need to do to install and run the service is run `./run.sh` in the root directory. (You will need python3 installed)

It will create a virtualenv and install pip dependencies on first run, and run the service on the first and consecutive runs.

Caveat: It seems that the test Fixer API key I've received only allows for gathering rates with EUR as the base currency. Best to make trades with that in mind.
