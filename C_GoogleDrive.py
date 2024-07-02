from A_Variables import *
from B_Decorators import Singleton,method_efficency,error_catcher

class GoogleDrive(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized: # moze self ovde
            GoogleDrive._initialized = True
            self.SCOPES = [ 'https://www.googleapis.com/auth/drive',
                            'https://www.googleapis.com/auth/drive.file',
                            'https://www.googleapis.com/auth/admin.directory.user',
                            'https://www.googleapis.com/auth/userinfo.email',
                            'openid'
                            ]
            self.creds = self.authenticate_google_drive()
            self.connection = build('drive', 'v3', credentials=self.creds)

    def authenticate_google_drive(self):
        creds = None
        token_path = 'www_token.pickle'
        creds_path = 'www_credentials.json'

        # Proverite da li postoji Token.pickle fajl koji čuva korisničke kredencijale
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        # Ako nema kredencijala ili su nevažeći, korisnik mora da se autentifikuje
        if not creds or not creds.valid:
            print('Refreshing credentials...')
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f'Error refreshing credentials: {e}')
                    # Briše token ako osvežavanje nije uspelo
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    creds = None
            if not creds:
                print('Running authentication flow...')
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Čuva kredencijale za sledeću upotrebu
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    def get_UserEmail(self):
        oauth2_service = build('oauth2', 'v2', credentials=self.creds)
        user_info = oauth2_service.userinfo().get().execute()
        return user_info.get('email')
    
    def get_FileInfo(self, file_id):
        file = self.connection.files().get(
            fileId=file_id, 
            fields='name, size, mimeType, imageMediaMetadata'
        ).execute()
        
        if 'imageMediaMetadata' in file:
            width = file['imageMediaMetadata'].get('width', 'Unknown')
            height = file['imageMediaMetadata'].get('height', 'Unknown')
            return {
                'name': file['name'],
                'size': file['size'],
                'mimeType': file['mimeType'],
                'width': width,
                'height': height
            }
        
        return {
            'name': file['name'],
            'size': file['size'],
            'mimeType': file['mimeType']
        }
    
    def get_video_dimensions(self,file_path):
        ffmpeg_path = 'D:/Work/4-Project/RHMH/SQLite/required_programs/ffprobe.exe'
        os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_path)
        probe = ffmpeg.probe(file_path)
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        if video_streams:
            width = video_streams[0]['width']
            height = video_streams[0]['height']
            return width, height
        else:
            return None, None

    def download_File(self, file_id, destination): # return je destination
        request = self.connection.files().get_media(fileId=file_id)
        with open(destination, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
    
    def download_BLOB(self, file_id):
        request = self.connection.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.getvalue()
   

    def upload_NewFile_asFile(self, file_name, GoogleDrive_folder, file_path, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.connection.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def upload_NewFile_asBLOB(self, file_name, GoogleDrive_folder, blob_data, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaIoBaseUpload(io.BytesIO(blob_data), mimetype=mime_type)
        file = self.connection.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    

    def upload_UpdateFile(self, file_id, file_path, mime_type):
        media = MediaFileUpload(file_path, mimetype=mime_type)
        self.connection.files().update(fileId=file_id, media_body=media).execute()
        return True

    def upload_UpdateFile_changeName(self, file_id, new_name):
        file_metadata = {'name': new_name}
        self.connection.files().update(
            fileId=file_id, 
            body=file_metadata
        ).execute()
        return True

    def delete_file(self, file_id):
        self.connection.files().delete(fileId=file_id).execute()
        return True

if __name__ == '__main__':

    user = GoogleDrive()
    user_email = user.get_UserEmail()
    print(user_email)
    ID = user.upload_UpdateFile(RHMH_DB['id'],'RHMH_test.db',RHMH_DB['mime'])
    print(ID)