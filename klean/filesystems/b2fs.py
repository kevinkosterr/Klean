from klean.filesystems.filesystem import Filesystem
from b2sdk.v2 import B2Api, InMemoryAccountInfo
from typing import List


class B2FS(Filesystem):
    def __init__(self, bucket: str, key_id: str, app_id: str) -> None:
        # holds all the account info in memory.
        info = InMemoryAccountInfo()
        self.api = B2Api(info)

        # authorize account through BackBlaze B2 API.
        self.b2 = self.api.authorize_account("production", key_id, app_id)
        self.bucket = self.api.get_bucket_by_name(bucket)
        self.filenames_to_obj_map = {}
        super().__init__()

    def get_sorted_files(self) -> List[str]:
        """ 
        Gets a sorted list of filenames. 
        :return: a sorted list of filenames
        """
        # putting the filenames as keys into a dictionary 
        # every value of a filename is a B2File object 
        self.filenames_to_obj_map = {_[0].file_name: _[0] for _ in self.bucket.ls()}
        filenames = self.filenames_to_obj_map.keys()
        return sorted(filenames, reverse=True)

    def delete_files(self, kill_list: List[str], verbose: bool = False) -> None:
        """ 
        Deletes the B2File objects based on the filenames in kill_list 
        :param kill_list: the kill_list extended by store_files_in_buckets()
        :param verbose: toggle verbosity
        """
        deleted_files = []
        for filename in kill_list:
            # refers to the empty dictionary defined in __init__ of this class 
            obj = self.filenames_to_obj_map[filename]
            self.api.delete_file_version(
                obj.id_, filename
            )
            deleted_files.append(filename)
        print(f'{len(deleted_files)} files have been deleted.')
