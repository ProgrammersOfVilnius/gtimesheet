def get_project_mapping(db):
    mapping = {}
    for row in db['times'].distinct('projectName', 'project'):
        mapping[row['projectName']] = int(row['project'])
    return mapping
