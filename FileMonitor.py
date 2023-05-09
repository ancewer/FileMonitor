# ！/usr/bin/env python
# -*-coding: UTF-8 -*-
# @Time : 2023/5/5 12:49
# @Author : Chunbo Liu
# @Email: ancewer@outlook.com
# @File : FileMonitor.py
# @Software: PyCharm
# To single file: pyinstaller -F --hidden-import="pydicom.encoders.gdcm" --hidden-import="pydicom.encoders.pylibjpeg" FileMonitor.py
# To package: pyinstaller -D --hidden-import="pydicom.encoders.gdcm" --hidden-import="pydicom.encoders.pylibjpeg" FileMonitor.py

from glob import glob
from configparser import ConfigParser
import os, shutil, subprocess
from pydicom import read_file
from datetime import datetime

def MonacoFiles(cf, f):
    source_dir = cf['Dir']['SourceDir']
    dcm_files = glob(os.path.join(source_dir, '*_Dose.dcm'))  # dose file
    if len(dcm_files) == 0:
        print('{} Found Nothing!'.format(datetime.now()))
        f.write('{} Found Nothing!\n'.format(datetime.now()))
    for dcm_file in dcm_files:
        # plan file
        plan = dcm_file.replace('_Dose', '')
        if os.path.exists(plan):  # plan file
            info = read_file(plan, force=True)
            TxMachine = info.BeamSequence[0].TreatmentMachineName
            new_folder = info.PatientID + '-' + str(info.PatientName) + '-' + info.RTPlanName
            to_dir = os.path.join(cf['Dir']['ToDir'], TxMachine)
            pat_folder = os.path.join(to_dir, new_folder)
            if not os.path.exists(pat_folder):
                os.mkdir(pat_folder)
                # os.system('mkdir {}'.format(pat_folder))
                print('{} create {}'.format(datetime.now(), pat_folder))
                f.write('{} create {}\n'.format(datetime.now(), pat_folder))
            shutil.move(dcm_file, os.path.join(pat_folder, os.path.basename(dcm_file)))
            print('{} moved {} to {}'.format(datetime.now(), dcm_file,
                                             os.path.join(pat_folder, os.path.basename(dcm_file))))
            f.write('{} moved {} to {}\n'.format(datetime.now(), dcm_file,
                                                 os.path.join(pat_folder, os.path.basename(dcm_file))))
            shutil.move(plan, os.path.join(pat_folder, os.path.basename(plan)))
            print('{} moved {} to {}'.format(datetime.now(), plan, os.path.join(pat_folder, os.path.basename(plan))))
            f.write(
                '{} moved {} to {}\n'.format(datetime.now(), plan, os.path.join(pat_folder, os.path.basename(plan))))
        else:
            print('{} Not found the corresponding plan file, will do nothing!'.format(datetime.now()))
            f.write('{} Not found the corresponding plan file, will do nothing!\n'.format(datetime.now()))

def TOMOFiles(cf, f):
    source_dir = cf['Dir']['TOMOSourceDir']
    dcm_files = glob(os.path.join(source_dir, 'RD*.dcm'))  # dose file
    if len(dcm_files) == 0:
        print('{} Found Nothing!'.format(datetime.now()))
        f.write('{} Found Nothing!\n'.format(datetime.now()))
    for dcm_file in dcm_files:
        dose_info = read_file(dcm_file, force=True)
        # plan file
        plan = os.path.join(source_dir, 'RP.' + dose_info.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID + '.dcm')
        print(plan)
        if os.path.exists(plan):  # plan file
            info = read_file(plan, force=True)
            TxMachine = info.BeamSequence[0].TreatmentMachineName
            new_folder = info.PatientID + '-' + str(info.PatientName).replace('^', ' ').strip() + '-' + info.RTPlanName
            to_dir = os.path.join(cf['Dir']['TOMOToDir'], TxMachine)
            pat_folder = os.path.join(to_dir, new_folder)
            if not os.path.exists(pat_folder):
                os.mkdir(pat_folder)
                # os.system('mkdir {}'.format(pat_folder))
                print('{} create {}'.format(datetime.now(), pat_folder))
                f.write('{} create {}\n'.format(datetime.now(), pat_folder))
            shutil.move(dcm_file, os.path.join(pat_folder, os.path.basename(dcm_file)))
            print('{} moved {} to {}'.format(datetime.now(), dcm_file,
                                             os.path.join(pat_folder, os.path.basename(dcm_file))))
            f.write('{} moved {} to {}\n'.format(datetime.now(), dcm_file,
                                                 os.path.join(pat_folder, os.path.basename(dcm_file))))
            shutil.move(plan, os.path.join(pat_folder, os.path.basename(plan)))
            print('{} moved {} to {}'.format(datetime.now(), plan, os.path.join(pat_folder, os.path.basename(plan))))
            f.write(
                '{} moved {} to {}\n'.format(datetime.now(), plan, os.path.join(pat_folder, os.path.basename(plan))))
        else:
            print('{} Not found the corresponding plan file, will do nothing!'.format(datetime.now()))
            f.write('{} Not found the corresponding plan file, will do nothing!\n'.format(datetime.now()))

def HandleFiles(cf, f):
    Machines = cf['Dir']['Machine'].split(',')
    print(Machines)
    for Machine in Machines:
        if Machine.__contains__('LA'):
            print('{} processing Monaco QA!'.format(datetime.now()))
            f.write('{} processing Monaco QA!\n'.format(datetime.now()))
            MonacoFiles(cf, f)
        elif Machine.__contains__('TOMO'):
            print('{} processing TOMO QA!'.format(datetime.now()))
            f.write('{} processing TOMO QA!\n'.format(datetime.now()))
            TOMOFiles(cf, f)
        else:
            print('{} Not Support {}!'.format(datetime.now(), Machine))
            f.write('{} Not Support {}!\n'.format(datetime.now(), Machine))


if __name__ == '__main__':
    print(datetime.now())
    cf = ConfigParser()
    cf.read('config.ini', encoding="utf-8-sig")
    print('Source Dir:{}'.format(cf['Dir']['SourceDir']))
    print('Source Dir:{}'.format(cf['Dir']['TOMOSourceDir']))
    print('Destination Dir:{}'.format(cf['Dir']['ToDir']))
    print('Destination Dir:{}'.format(cf['Dir']['TOMOToDir']))
    f = open('log.txt', 'a')
    try:
        # subprocess.call(r'net use * /del /y')
        # subprocess.call(r'net use {} {} /user:{}'.format(cf['Dir']['TOMOSourceDir'], cf['Dir']['TOMOSourceDir_Account'].split()[1], cf['Dir']['TOMOSourceDir'].split()[0]),shell=True)  # connect with network drive
        # subprocess.call(r'net use {} {} /user:{}'.format(cf['Dir']['ToDir'], cf['Dir']['ToDir_Account'].split()[1], cf['Dir']['ToDir_Account'].split()[0]),shell=True)  # connect with network drive
        # subprocess.call(r'net use {} {} /user:{}'.format(cf['Dir']['TOMOToDir'], cf['Dir']['TOMOToDir_Account'].split()[1], cf['Dir']['TOMOToDir_Account'].split()[0]),shell=True)  # connect with network drive
        HandleFiles(cf, f)
    except Exception as e:
        print(e)
        f.write(str(e) + '\n')
        f.close()



