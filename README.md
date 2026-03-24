# Everpure MOC

This repository stores the files and instructions for configuring Everpure storage for MOC clusters.

## Prerequisites 

To reach the Pure Storage webpage running in MOC you will need to have login creds created for you ahead of time. 

## Configuring a storage server

In order to enable a storage endpoint accesible from an OpenShift cluster, you must first configure a handful of critical items in Pure. 

1. Choose a realm under which to work (Or create a new realm if needed)
2. Create a filesystem 
3. Create a server
4. Create a filesystem export from server configuration page
5. Create an interface on the DATA subnet
6. Configure DNS for the server created above
7. Create a new user for the cluster and attach the storage_admin policy

## Install Portworx on OCP 

### Prerequisites 

1. Create an account at [https://central.portworx.com/](https://central.portworx.com/)
2. See [portworx system requirements](https://docs.portworx.com/portworx-csi/system-requirements#network-requirements)

### Generate Portworx spec

1. At [central.portworx.com](central.portworx.com) create a new yaml spec by selecting PX-CSI and fill out the OCP cluster details. 
2. Aplly the file in the cluster.

Here is a sample yaml with some options and descriptions

### Install Portworx operator in cluster

In the OCP cluster create the namespace:
`oc create namespace portworx`

See [Portworx csi system requirements](https://docs.portworx.com/portworx-csi/system-requirements) prior to installing the operator. 

Install the operator using the OCP operators tab, installing the operator in namespace portworx. 

### Validate Portworx operator install

Verify operator pods are running: 
`oc get pods -n portworx -o wide | grep -e portworx -e px`

Get status of portworx cluster:
`oc get stc -n portworx`

Check for newly created storage classes: 
`oc get sc`

You should see something like this if using the defaults: 
```
px-csi-db                                        pxd.portworx.com                        Delete          Immediate              true                   4d4h
px-csi-db-cloud-snapshot                         pxd.portworx.com                        Delete          Immediate              true                   24d
px-csi-db-cloud-snapshot-encrypted               pxd.portworx.com                        Delete          Immediate              true                   24d
px-csi-db-encrypted                              pxd.portworx.com                        Delete          Immediate              true                   24d
px-csi-db-local-snapshot                         pxd.portworx.com                        Delete          Immediate              true                   24d
px-csi-db-local-snapshot-encrypted               pxd.portworx.com                        Delete          Immediate              true                   24d
px-csi-replicated                                pxd.portworx.com                        Delete          Immediate              true                   24d
px-csi-replicated-encrypted                      pxd.portworx.com                        Delete          Immediate              true                   24d
px-fa-direct-access                              pxd.portworx.com                        Delete          Immediate              true                   4d21h
px-fb-direct-access-nfsv3                        pxd.portworx.com                        Delete          Immediate              true                   4d21h
px-fb-direct-access-nfsv4                        pxd.portworx.com                        Delete          Immediate              true                   4d21h
```




