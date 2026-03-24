# Everpure MOC

This repository stores the files and instructions for configuring Everpure storage for MOC clusters.

## Prerequisites

To access the Pure Storage web interface running in MOC, you must have login credentials created for you ahead of time.

## Getting Started

To enable a storage endpoint accessible from an OpenShift cluster, you must first configure several critical items in Pure:

- Create a new user for the cluster and attach the `storage_admin` policy
- Choose a realm under which to work (or create a new realm if needed)
- Create a filesystem
- Create a server
- Create a filesystem export from the server configuration page
- Create an interface on the data subnet
- Configure DNS for the server created above

### Creating a User

In the Pure GUI, open the options menu and select `Users`.

Create a new user and complete the form. Once the user account is created, assign the `storage_admin` policy from the list.

This account can now create and manage storage resources.

### Create a realm for your cluster

From the Pure dashboard, click storage and navigate to the realms tab. From here create a new realm or select one for the cluster you're working with. A best practice suggested by Everpure folks is to have a realm per cluster, this way we can easily manage different rbac and enforment independantly. 

### Create a filesystem in your realm

In your realm, find the `File Systems` button. From here you will determine the size, type, enabled protocols, and name your file system.

### Create a server 

Again select your realm, then create a new server to host your file system. From here a window will pop up walking you through the process. You will be prompted to create a virtual interface and choose an address for it (make sure to assign the correct data subnet here). This is the endpoint you will hand to OCP later for nfs access. 

### Create a file system export

Once that is created, click your filesystem and click the plus iocn in the file system exports box. Make sure your file system export is realm scoped, and choose the appropriate export policy.

## Install Portworx on OCP

### Prerequisites

1. Create an account at https://central.portworx.com/
2. Review the Portworx system requirements: https://docs.portworx.com/portworx-csi/system-requirements#network-requirements

### Generate Portworx Spec

1. At https://central.portworx.com, create a new YAML spec by selecting PX-CSI and filling out the OCP cluster details.
2. Apply the generated file to the cluster.

Here is a sample YAML with some options and descriptions:

### Install Portworx Operator in Cluster

In the OCP cluster, create the namespace:
`oc create namespace portworx`

Review the Portworx CSI system requirements prior to installing the operator:
https://docs.portworx.com/portworx-csi/system-requirements

Install the operator using the OCP Operators tab, selecting the `portworx` namespace.

### Validate Portworx Operator Installation

Verify operator pods are running:
`oc get pods -n portworx -o wide | grep -e portworx -e px`


Get the status of the Portworx cluster:
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

