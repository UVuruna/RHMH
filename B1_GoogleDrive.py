from A1_Variables import *

class GoogleDrive:
    SCOPES = [ 'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/userinfo.email',
                'openid'
                ]
    creds = None
    connection:build = None
    
    @staticmethod
    def setup_connection() -> None:
        GoogleDrive.creds = GoogleDrive.authenticate_google_drive()
        GoogleDrive.connection = build('drive', 'v3', credentials=GoogleDrive.creds)

    @staticmethod
    def authenticate_google_drive():
        creds = None
        token_path = os.path.join(directory,'www_token.pickle')
        creds_path = os.path.join(directory,'www_credentials.json')

        # Proverite da li postoji Token.pickle fajl koji čuva korisničke kredencijale
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    creds = None
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, GoogleDrive.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    @staticmethod
    def get_UserEmail():
        oauth2_service = build('oauth2', 'v2', credentials=GoogleDrive.creds)
        user_info = oauth2_service.userinfo().get().execute()
        return user_info.get('email')
    
    @staticmethod
    def get_FileInfo(file_id):
        file = GoogleDrive.connection.files().get(
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
    
    '''
    @staticmethod
    def get_video_dimensions(file_path):
        ffmpeg_path = 'required_programs/ffprobe.exe'
        os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_path)
        probe = ffmpeg.probe(file_path)
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        if video_streams:
            width = video_streams[0]['width']
            height = video_streams[0]['height']
            return width, height
        else:
            return None, None
    #'''

    @staticmethod
    def download_DB(file_id, destination:str):
        temp_destination = destination.split('.')[0] + '_progress.db'
        request = GoogleDrive.connection.files().get_media(fileId=file_id)
        with open(temp_destination, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        os.remove(destination)
        os.rename(temp_destination, destination)
    
    @staticmethod
    def download_BLOB(file_id):
        try:
            request = GoogleDrive.connection.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return fh.getvalue()
        except RuntimeError:
            raise
   
    @staticmethod
    def upload_NewFile_asFile(file_name, GoogleDrive_folder, file_path, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = GoogleDrive.connection.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    @staticmethod
    def upload_NewFile_asBLOB(file_name, GoogleDrive_folder, blob_data, mime_type):
        file_metadata = {'name': file_name, 'parents': GoogleDrive_folder}
        media = MediaIoBaseUpload(io.BytesIO(blob_data), mimetype=mime_type)
        file = GoogleDrive.connection.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    
    @staticmethod
    def upload_UpdateFile(file_id, file_path, mime_type):
        media = MediaFileUpload(file_path, mimetype=mime_type)
        GoogleDrive.connection.files().update(fileId=file_id, media_body=media).execute()
        return True

    @staticmethod
    def upload_UpdateFile_changeName(file_id, new_name):
        file_metadata = {'name': new_name}
        GoogleDrive.connection.files().update(
            fileId=file_id, 
            body=file_metadata
        ).execute()
        return True

    @staticmethod
    def delete_file(file_id):
        GoogleDrive.connection.files().delete(fileId=file_id).execute()
        return True

if __name__ == '__main__':
    GoogleDrive.setup_connection()
    #GoogleDrive.download_DB(RHMH_dict['id'],RHMH_dict['path'])
    #GoogleDrive.upload_UpdateFile(RHMH_dict['id'],RHMH_dict['path'],RHMH_dict['mime'])
    GoogleDrive.upload_UpdateFile(LOGS_dict['id'],LOGS_dict['path'],LOGS_dict['mime'])
