import os, shutil
from workflow import web, Workflow3


DIR_CACHE_IMAGE = './cache'
CACHE_LIMIT = 500 #limits number of files.


def put(film_id, url):
    if is_cache_full(DIR_CACHE_IMAGE):
        Workflow3().logger.debug("deleting cache")
        clear(DIR_CACHE_IMAGE, CACHE_LIMIT / 2)
    try:
        _, ext = os.path.splitext(os.path.basename(url))
        filepath = os.path.join(DIR_CACHE_IMAGE, film_id)#, ext) # <- Let's try without extension it might work :)
        web.get(url).save_to_path(filepath)
        return filepath
    except Exception as e:
        raise e


def get(film_id):
    filepath = os.path.join(DIR_CACHE_IMAGE, film_id)
    return filepath if os.path.isfile(filepath) else None


def is_cache_full(dir = DIR_CACHE_IMAGE):
    return len(get_cached_files_by_access_date(dir)) > CACHE_LIMIT


def get_cached_files_by_access_date(dir):
    list_of_files = os.listdir(dir)
    full_path_list = [os.path.join(dir, x) for x in list_of_files if not x.endswith('log')]
    full_path_list.sort(key=os.path.getatime)
    return full_path_list


def clear(dir = DIR_CACHE_IMAGE, n = None):
    file_list = get_cached_files_by_access_date(dir)
    if n is not None:
        file_list = file_list[:n]

    for file_path in file_list:
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def clear_workflow_cache():
    Workflow3().clear_cache()
