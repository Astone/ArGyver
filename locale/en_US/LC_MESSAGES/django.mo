��          4      L       `   )   a      �   7  �   �   �  v   �                    AGV_EXCEPTION_LOCATION_ROOT_FOLDER_EXISTS AGV_WARNING_RSYNC_ARGUMENTS Project-Id-Version: 4.0.0
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2015-01-03 22:44+0100
PO-Revision-Date: 2015-01-03 18:00+0000
Last-Translator: Bram Stoeller <bram@stoeller.nl>
Language-Team: English
Language: Anglish
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 Someone tried to create a new location. The slug of a location defines the root folder of the corresponding archive and according to the database this root folder already exists. This should definitely not happen. Only use this if you know what you are doing, it might break the ArGyver. Using -exclude and --include should be fine. 