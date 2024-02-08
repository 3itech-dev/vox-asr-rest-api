# 3i VOX ASR REST API python example

###### Install the requirements
`python3 -m pip install -r requirements.txt`

###### Generate access_token at 3i-vox.ru
Request:
```
curl -X POST "https://3i-vox.ru/oauth/token/" \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"password","username":"<USERNAME>","password":"<PASSWORD>","client_id":"<CLIENT_ID>","client_secret":"<CLIENT_SECRET>"}'
```
`<USERNAME>`, `<PASSWORD>` - your 3i-vox.ru login credentials.\  
`<CLIENT_ID>`, `<CLIENT_SECRET>` - you can get in your account settings at 3i-vox.ru.

Response:\
`{"token_type":"Bearer","access_token":"<ACCESS_TOKEN>","scope":"vox"}`\
`<ACCESS_TOKEN>` - access token for further commands

### Run asr rest api example

```
usage: python3 3i_vox_asr_rest_api.py [-h] --model MODEL --file FILE 
                                     [--token TOKEN] [--off_print_result]
                                     [--on_save_result] [--punctuation]

  -h, --help          show this help message and exit
  --model MODEL       Model name
  --file FILE         File name
  --token TOKEN       OAuth access token
  --off_print_result  Disables console output
  --on_save_result    Enable saving the result to a file
  --punctuation       Enable automatic punctuation
```

###### Output the result only to the console
`python3 3i_vox_asr_rest_api.py --token=<ACCESS_TOKEN> --model=<MODEL> --file=<FILE>`

###### Save the result only to a file
`python3 3i_vox_asr_rest_api.py --token=<ACCESS_TOKEN> --model=<MODEL> --file=<FILE> --off_print_result --on_save_result`

###### Output to the console and save the result to a file
`python3 3i_vox_asr_rest_api.py --token=<ACCESS_TOKEN> --model=<MODEL> --file=<FILE> --on_save_result`


The processed audio will be saved as ```<FILE_NAME>```.txt <br>
```<FILE_NAME>``` - the name of the ```<FILE>``` that was sent for processing.
