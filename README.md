# Everpure MOC

This repository stores the files and instructions for configuring Everpure storage for MOC clusters.

## Prerequisites

To access the Pure Storage web interface running in MOC, you must have login credentials created for you ahead of time.

## Quickstart

To enable a storage endpoint accessible from an OpenShift cluster, you must first configure several critical items in Pure:

- Create a new user for the cluster and attach the `storage_admin` policy
- Choose a realm under which to work (or create a new realm if needed)
- Create a filesystem
- Create a server
- Create a filesystem export from the server configuration page
- Create an interface on the data subnet
- Configure DNS for the server created above
- Install/Configure Portworx operator

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

3. Create a file called `pure.json`, which will look like this:
```
  {
    "FlashBlades": [
      {
    "MgmtEndPoint": "FB end point 1",
    "APIToken": "<api-token-for-fb-management-endpoint1>",
    "NFSEndPoint": "<fb-nfs-endpoint>",
    "Labels": {
      "topology.portworx.io/zone": "<zone-1>",
      "topology.portworx.io/region": "<region-1>"
    }
  },
    {
    "MgmtEndPoint": "FB end point 2",
    "APIToken": "<api-token-for-fb-management-endpoint2>",
    "NFSEndPoint": "<fb-nfs-endpoint2>",
    "Labels": {
      "topology.portworx.io/zone": "<zone-1>",
      "topology.portworx.io/region": "<region-2>"
    }
  }
  ]
  }
```

4. Create a secret with the `pure.json` file:
`oc create secret generic px-pure-secret --namespace portworx --from-file=pure.json=<file path>`

This will hand the Flashblade details to the portworx operator, allowing a connection.

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

These are the 3 options you can use out of the box:
```
px-csi-db                                        pxd.portworx.com                        Delete          Immediate              true                   4d4h
px-fb-direct-access-nfsv3                        pxd.portworx.com                        Delete          Immediate              true                   4d21h
px-fb-direct-access-nfsv4                        pxd.portworx.com                        Delete          Immediate              true                   4d21h
```

### [Create a Custom `storageClass`](https://docs.portworx.com/portworx-csi/provision-storage/dynamic-provisioning/flashblade-file-systems#optional-create-a-custom-storageclass) to Consume Pure Storage

To configure a single NFS endpoint, use the following StorageClass specification:
`**NOTE**: This assumes the nfs endpoint is the same as the one provided to the k8s secret px-pure-secret`

```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-csi-fb
provisioner: pxd.portworx.com
parameters:
  backend: "pure_file"
  pure_export_rules: "*(rw)"
mountOptions:
  - nfsvers=3
  - tcp
allowVolumeExpansion: true
allowedTopologies:
  - matchLabelExpressions:
    - key: topology.portworx.io/zone
      values:
        - <zone-1>
    - key: topology.portworx.io/region
      values:
        - <region-1>
```

### Provisioning Storage Volumes

#### Filesystem Storage (NFS)

There are 2 different methods to provision storage in a Pure filesystem server:

1. [static provisioning of volumes](https://docs.portworx.com/portworx-csi/provision-storage/static-provisioning)

With this method, you must first create a filesystem in Pure first.

To import an existing volume, you must add annotations to your PVC that specify:

- portworx.io/pure-volume-name (required): The name of the existing volume on the Everpure storage array.
  - For FlashBlade file systems: filesystem_name
- portworx.io/pure-array-id (optional): The ID of the array where the volume exists. Use this to specify which array to import the volume from when multiple arrays are connected to your cluster.

The `pvc` spec will look something like:

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: preprovisioned-fb-pvc
  annotations:
    portworx.io/pure-volume-name: "<existing-filesystem-name>"
    # portworx.io/pure-array-id: "<your-flashblade-id>"  # Optional: specify array ID if you want to import the volume from specific array
spec:
  storageClassName: px-fb-direct-access-nfsv3
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Ti  # Must match the size of the existing file system on FlashBlade
```

2. [dyanamic provisioning of volumes](https://docs.portworx.com/portworx-csi/provision-storage/dynamic-provisioning) (default)

This is the default way to manage creation and allocation of pvcs. A `pvc` created in OpenShift will create a filesystem within the flashblade server via the chosen `storageClass`.

#### S3 Storage

To attach an s3 storage bucket to an OpenShift deployment the following must be done:

In the Pure server:

1. In the `Object Store` menu under storage, create a new account 
2. Create a new account export assigning the appropriate export policy. 
3. Click on the newly created account and create a new user
4. Click on the newly created user and create a new accessKey
5. Save the accessKey and accessKeyID 

Login to the OCP cluster and create a secret with all the s3 info:

```
oc create secret generic s3-access-secret \
  --from-literal=AWS_ACCESS_KEY_ID='<ACCESS_KEY>' \
  --from-literal=AWS_SECRET_ACCESS_KEY='<SECRET_KEY>' \
  --from-literal=AWS_ENDPOINT_URL=<DATA_VIP> \

```

Confirm access using a pod like the one below:

```
apiVersion: v1
kind: Pod
metadata:
  name: s3-debug
spec:
  restartPolicy: Never
  containers:
  - name: aws-cli
    image: amazon/aws-cli:latest
    command: ["/bin/sh", "-c"]
    args:
      - sleep infinity
    envFrom:
    - secretRef:
        name: s3-access-secret
```

In the pod run: `aws --endpoint-url="$AWS_ENDPOINT_URL" --no-verify-ssl s3 ls`

If the connection is successful you'll see your bucket, in this case named test:
```
2026-04-15 16:56:30 test
```

There is no direct csi object provided by Portworx to configure/claim S3 buckets at this time. Communication to S3 buckets must be handled directly by making API calls. More information can be found in the [Flashblade Object Store Documentation](https://support.purestorage.com/bundle/m_purityfb_rest_api/page/FlashBlade/Purity_FB/PurityFB_REST_API/S3_Object_Store_REST_API/topics/concept/c_flashblade_object_store_documentation_s3_api.html)

### Pure1

[Pure1](https://pure1.purestorage.com/) is an integrated management suite available by web browser, provided by Everpure. Accounts and permissions are managed by the Everpure team, and any users will have to register before being able to access this service. 

There are lots of built in tools here from automation, Everpure software updates, data security, and a [ticket based support system](https://supportcenter.purestorage.com/) which we have already made use of. Responses were reasonably quick from the Everpure service team with multiple reponses per day and a 1-on-1 debug session in less than 24hrs. 

Security assesments are available from here and CVEs are listed here. 

TODO: create a separate document for managing Pure1 if necessary & and determine how we can leverage it. 

### Troubleshooting 

We ran into issues with `pvc`s created under portworx `storageClasses` mounting in `pod`s. In pod events this manifested as an `event` with the error message: "No valid backend found for ArrayID d663994a-a52c-49ac-bcff-2b4de120192d: not found". This may have been related to network asymmetry, though fixing the network issue was not an immediate fix. Eventually, bouncing the px-pure-csi-controller 'pods' one at a time in the portworx `namespace` did result in `pvc`s mounting and `pod`s creating. More info can be found in this [ticket](https://supportcenter.purestorage.com/cases/1f896c5f3b408f18b7a1c41864e45a2f). 