# Everpure MOC

This repository stores the files and instructions for configuring Everpure storage for MOC clusters.

## Prerequisites

To access the Pure Storage web interface running in MOC, you must have login credentials created for you ahead of time.

## Getting Started

To enable a storage endpoint accessible from an OpenShift cluster, you must first configure several critical items in Pure:

1. Choose a realm under which to work (or create a new realm if needed)
2. Create a filesystem
3. Create a server
4. Create a filesystem export from the server configuration page
5. Create an interface on the data subnet
6. Configure DNS for the server created above
7. Create a new user for the cluster and attach the `storage_admin` policy

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


### Creating a User

In the Pure GUI, open the options menu and select `Users`.

Create a new user and complete the form. Once the user account is created, assign the `storage_admin` policy from the list.

This account can now create and manage storage resources.

