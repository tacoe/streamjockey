# Sencha Touch 2 Native Packaging for iOS on Mac

## Requirements

### Software

  - Mac OS X 10.6+
  - Xcode (required for for iOS Simulator)

### Apple iOS provisioning

  - Complete iOS provisioning on the [Apple iOS provisioning portal][1] and have the certificates and devices setup through the provisioning portal and Xcode.
  - Create an App ID and finish provisioning your application. Please refer to the How-To section in the [Apple iOS provisioning portal][1] for help.

Note: You will need to know your App ID and App Name to complete the packaging
process.

## Steps to package your application for iOS on Mac

  1. Prerequisite: Complete iOS provisioning on [Apple iOS provisioning portal][1].
  2. Install the packager, part of Sencha SDK Tools 2.0
  3. Create a packaging configuration file to be use with the native packager.
  4. Run the packager to create a packaged <application>.app.

### Step 1: Complete iOS provisioning on Apple iOS provisioning portal for the application

Please use the [Apple iOS provisioning portal][1] to setup the appropriate
development and distribution certifications and profiles.

### Step 2: Install the packager

  - Run the Sencha SDK installation: SenchaSDKTools (SenchaSDKTools-2.0.0-Beta)** **
  - The sencha command that includes the package option will be installed to the specified location during installation (default: Applications/SenchaSDKTools-2.0.0-Beta/command).**

### Step 3: Create a packaging configuration file to be use with the native packager.

The configuration file has the following format:

    {
        "applicationName": "<AppName>",
        "applicationId": "<AppID>",
        "outputPath": "<AppPackageOutputPath>",
        "iconName": "<AppIconName>",
        "versionString": "<AppVersion>",
        "webAppPath": "<PathToWebApp>",
        "configuration": "<Release | Debug>",
        "platform": "<iOSSimulator | iOS>",
        "deviceType": "<iPhone | iPad | Universal>",
        "certificateAlias": "<(Optional)CertificateAlias>",
        "orientations": [
            "portrait",
            "landscapeLeft",
            "landscapeRight",
            "portraitUpsideDown"
        ]
    }

Note: A configuration file template can be created by running the following
command in the Terminal:

    sencha package generate <configTemplate.json>

`<configTemplate.json>` is the name of the configuration file.
Note: the `<configTemplate.json>` path or filename cannot contain any space.

The following parameters are applicable to iOS packaging:

    "applicationName":"<AppName>"

Both AppName and AppID can be found on the [iOS provisioning portal][1] on the
App IDs section.

{@img idScreen.png App ID}

E.g. from above,

  - AppName is “Sencha Touch 2 Packaging”
  - AppID is “com.Sencha.Touch2Packaging”

Note: the App ID is the same as the one you put in the Identifier field in
Xcode.

    "applicationId":"<AppID>"

    "outputPath":"<AppPackageOutputPath>"

The output location of the packaged application, <application.app>.

    "iconName":"<AppIconName>"

The icon file to be used for your application.


Note: Retina icon should be specified with @2x at the end of the icon name.
For example icon.png (regular) and icon@2x.png (retina). If a retina icon with
the <Icon Name>@2x.png exists, the packager will include the retina icon.


Note: Please refer to the [iOS icon guideline][3] for further information on
icon file specifications.

    "versionString":"<AppVersion>",

The version of the application.

    "webAppPath":"<PathToWebApp>"

The path of the web application to be packaged.

    "configuration":"<Release | Debug>"

Specify build type: Release or Debug.

    "platform":"<Simulator | iOS>"

Specify if the build is for the iOS simulator (iOSSimulator) or for the device
(iOS).


Note: the iOS simulator cannot run a signed build. A signed build can only be
run on the device.

    "deviceType":"<iPhone | iPad | Universal>"

Specify device type.

Available options:
 - iPhone: for iPhone applications
 - iPad: for iPad applications
 - Universal: for both iPhone and iPad applications

    "certificateAlias":"<(Optional)CertificateAlias>"

This is an optional configuration. You can specify a specific Certificate
Alias to use for signing your application.


Note: If omitted, the default certificate used is the one you setup in iOS
Provisioning Portal.

    "orientations": [
        "portrait",
        "landscapeLeft",
        "landscapeRight",
        "portraitUpsideDown"
    ]

This is an optional configuration. You can specify the orientations of the application.
Available options: “portrait”, “landscapeLeft”, “landscapeRight” and “portraitUpsideDown”

Note: If omitted, the default orientations are all four orientations.

**Sample debug configuration file**

    {
        "applicationName":"Sencha Touch 2 Packaging",
        "applicationId":"com.sencha.touch2packaing",
        "iconName":"icon.png",
        "versionString":"1.0",
        "outputPath":"~/Desktop/STBuild-iOS",
        "webAppPath":"~/Desktop/www/",
        "configuration":"Debug",
        "platform":"iOSSimulator",
        "deviceType":"iPhone",
        "orientations": [
            "portrait",
            "landscapeLeft",
            "landscapeRight",
            "portraitUpsideDown"
        ]
    }

**Sample release configuration file**

    {
        "applicationName":"Sencha Touch 2 Packaging",
        "applicationId":"com.sencha.touch2packaing",
        "iconName":"icon.png",
        "versionString":"1.0",
        "outputPath":"~/Desktop/STBuild-iOS",
        "webAppPath":"~/Desktop/www/",
        "configuration":"Release",
        "platform":"iOS",
        "deviceType":"iPhone",
        "orientations": [
            "portrait",
            "landscapeLeft",
            "landscapeRight",
            "portraitUpsideDown"
        ]
    }

## Step 4: Run the packager to create the packaged application

**Packaging a debug application and run it on the iOS simulator**

Prerequisite*:* The Platform and Configuration setting needs to be set in the
config file.

Example:

    "platform":"iOSSimulator"
    "configuration":"Debug"

Note: if the Platform and Configuration settings are not provisioned,  iOS
will not run the application correctly.

To package a debug/unsigned application to run on the iOS simulator, issue the
following command in Terminal:

    sencha package run <configFile.json>

The iOS simulator with the application running will launch after successful
executing this command.

Note: the “deviceType” identifier will trigger the appropriate simulator:
iPhone or iPad.

**Packaging the application to deploy on the iOS device**

To package a signed application to run on the device, issue the following
command in Terminal:

    sencha package <configFile.json>

Note: an <AppName.app> is created in the specified output location. This is
the application that you can use to deploy to the iOS device.

**See Also**

  1. [Apple iOS provisioning portal][1]
  2. [iOS Icon guideline][4]

[1]: https://developer.apple.com/ios/manage/overview/index.action
[3]: http://developer.apple.com/library/ios/%23documentation/iPhone/Conceptual/iPhoneOSProgrammingGuide/BuildTimeConfiguration/BuildTimeConfiguration.html%23//apple_ref/doc/uid/TP40007072-CH7-SW1
[4]: http://developer.apple.com/library/ios/%23documentation/userexperience/conceptual/mobilehig/IconsImages/IconsImages.html

