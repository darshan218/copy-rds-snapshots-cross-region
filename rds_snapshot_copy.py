#!/usr/bin/python
import boto3
import operator

ACCOUNT     = 'your-accound-id'

dictRegion  = {
                'region1':  {'srcRegion': 'your-source-region', 'destRegion': 'your-destination-region', 'databases': ["your-database-name"], 'kmsKey': 'arn:aws:kms:us-west-2:123456890:key/123456890-1234-1234-1234-123456890'},
                'region2' :  {'srcRegion': 'your-source-region', 'destRegion': 'your-destination-region', 'databases': ["your-database-name", "your-database-name"], 'kmsKey': 'arn:aws:kms:eu-central-1:123456890:key/123456890-1234-1234-1234-123456890' }
            }

def copy_latest_snapshot():

    for strKey, dictValue in dictRegion.items():
        objSrcClient = boto3.client('rds', region_name=dictValue['srcRegion'])
        objDestClient = boto3.client('rds', region_name=dictValue['destRegion'])

        for dictDatabase in dictValue['databases']:
            strResponse = objSrcClient.describe_db_snapshots(
                DBInstanceIdentifier=dictDatabase,
                IncludePublic=False,
                IncludeShared=True,
                SnapshotType='Automated',
            )

            if len(strResponse['DBSnapshots']) == 0:
                    raise Exception("No automated snapshots found")

            dictDatabaseSnapshots = {}
            for dictSnapshot in strResponse['DBSnapshots']:
                if dictSnapshot['Status'] != 'available':
                    continue

                if dictSnapshot['DBInstanceIdentifier'] not in dictDatabaseSnapshots.keys():
                    dictDatabaseSnapshots[dictSnapshot['DBInstanceIdentifier']] = {}

                dictDatabaseSnapshots[dictSnapshot['DBInstanceIdentifier']][dictSnapshot['DBSnapshotIdentifier']] = dictSnapshot[
                    'SnapshotCreateTime']

            for dictDatabase in dictDatabaseSnapshots:
                    listDbSorted = sorted(dictDatabaseSnapshots[dictDatabase].items(), key=operator.itemgetter(1), reverse=True)
                    strDbSnapshotName = dictDatabase + "-" + listDbSorted[0][1].strftime("%Y-%m-%d-%H-%M")

                    try:
                        objDestClient.describe_db_snapshots(
                            DBSnapshotIdentifier=strDbSnapshotName
                        )
                    except:
                        strResponse = objDestClient.copy_db_snapshot(
                            SourceDBSnapshotIdentifier='arn:aws:rds:'+ dictValue['srcRegion'] +':' + ACCOUNT + ':snapshot:' + listDbSorted[0][0],
                            TargetDBSnapshotIdentifier=strDbSnapshotName,
                            CopyTags=True,
                            KmsKeyId=dictValue['kmsKey'],
                            SourceRegion=dictValue['srcRegion']
                        )

                        if strResponse['DBSnapshot']['Status'] != "pending" and strResponse['DBSnapshot']['Status'] != "available":
                            raise Exception("Copy operation for " + strDbSnapshotName + " failed!")
                        print("Copied " + strDbSnapshotName)

                        continue
                    print(f'{ strDbSnapshotName } Already copied')

def remove_old_snapshots():
  
    for strKey, dictValue in dictRegion.items():
        objDestClient = boto3.client('rds', region_name=dictValue['destRegion'])

        strResponse = objDestClient.describe_db_snapshots(
                SnapshotType='manual'
        )

        if len(strResponse['DBSnapshots']) == 0:
            raise Exception("No manual snapshots found")

        dictDatabaseSnapshots = {}
        for dictSnapshot in strResponse['DBSnapshots']:
            if dictSnapshot['Status'] != 'available':
                continue

            if dictSnapshot['DBInstanceIdentifier'] not in dictDatabaseSnapshots.keys():
                dictDatabaseSnapshots[dictSnapshot['DBInstanceIdentifier']] = {}

            dictDatabaseSnapshots[dictSnapshot['DBInstanceIdentifier']][dictSnapshot['DBSnapshotIdentifier']] = dictSnapshot['SnapshotCreateTime']

        for dictDatabase in dictDatabaseSnapshots:
            if len(dictDatabaseSnapshots[dictDatabase]) > 1:
                listDbSorted = sorted(dictDatabaseSnapshots[dictDatabase].items(), key=operator.itemgetter(1), reverse=True)
                listDbSnapshots = [ strDbSnapshot[0] for strDbSnapshot in listDbSorted[1:]]

                for listSnapshot in listDbSnapshots:
                    print("Removing " + listSnapshot)
                    objDestClient.delete_db_snapshot(
                        DBSnapshotIdentifier=listSnapshot
                    )

if __name__ == '__main__':
    copy_latest_snapshot()
    remove_old_snapshots()
