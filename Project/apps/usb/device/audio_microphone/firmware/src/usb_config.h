/********************************************************************
 FileName:  usb_config.h
 Processor: PIC16, PIC18, PIC24, or dsPIC USB Microcontrollers
 Complier:  Microchip XC8/C18/XC16
 Company:   Microchip Technology, Inc.

 Software License Agreement:

 The software supplied herewith by Microchip Technology Incorporated
 (the "Company") for its PIC(R) Microcontroller is intended and
 supplied to you, the Company's customer, for use solely and
 exclusively on Microchip PIC Microcontroller products. The
 software is owned by the Company and/or its supplier, and is
 protected under applicable copyright laws. All rights are reserved.
 Any use in violation of the foregoing restrictions may subject the
 user to criminal sanctions under applicable laws, as well as to
 civil liability for the breach of the terms and conditions of this
 license.

 THIS SOFTWARE IS PROVIDED IN AN "AS IS" CONDITION. NO WARRANTIES,
 WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT NOT LIMITED
 TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 PARTICULAR PURPOSE APPLY TO THIS SOFTWARE. THE COMPANY SHALL NOT,
 IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL OR
 CONSEQUENTIAL DAMAGES, FOR ANY REASON WHATSOEVER.
 *******************************************************************/

/*********************************************************************
 * Descriptor specific type definitions are defined in: usbd.h
 ********************************************************************/

#ifndef USBCFG_H
#define USBCFG_H

#include "system_config.h"

/** DEFINITIONS ****************************************************/
#define USB_EP0_BUFF_SIZE           8   // Valid Options: 8, 16, 32, or 64 bytes.
                                        // Using larger options take more SRAM, but
                                        // does not provide much advantage in most types
                                        // of applications.  Exceptions to this, are applications
                                        // that use EP0 IN or OUT for sending large amounts of
                                        // application related data.
                                    
#define USB_MAX_NUM_INT             1   // For tracking Alternate Setting
#define USB_MAX_EP_NUMBER           1

//Device descriptor - if these two definitions are not defined then
//  a ROM USB_DEVICE_DESCRIPTOR variable by the exact name of device_dsc
//  must exist.
#define USB_USER_DEVICE_DESCRIPTOR &device_dsc
#define USB_USER_DEVICE_DESCRIPTOR_INCLUDE extern const USB_DEVICE_DESCRIPTOR device_dsc

//Configuration descriptors - if these two definitions do not exist then
//  a ROM BYTE *ROM variable named exactly USB_CD_Ptr[] must exist.
//#define USB_USER_CONFIG_DESCRIPTOR USB_CD_Ptr
//#define USB_USER_CONFIG_DESCRIPTOR_INCLUDE extern ROM BYTE *ROM USB_CD_Ptr[]

//Make sure only one of the below "#define USB_PING_PONG_MODE"
//is uncommented.
//#define USB_PING_PONG_MODE USB_PING_PONG__NO_PING_PONG
#define USB_PING_PONG_MODE USB_PING_PONG__FULL_PING_PONG
//#define USB_PING_PONG_MODE USB_PING_PONG__EP0_OUT_ONLY
//#define USB_PING_PONG_MODE USB_PING_PONG__ALL_BUT_EP0     //NOTE: This mode is not supported in PIC18F4550 family rev A3 devices


#define USB_POLLING
//#define USB_INTERRUPT

/* Parameter definitions are defined in usb_device.h */
#define USB_PULLUP_OPTION USB_PULLUP_ENABLE
//#define USB_PULLUP_OPTION USB_PULLUP_DISABLED

#define USB_TRANSCEIVER_OPTION USB_INTERNAL_TRANSCEIVER
//External Transceiver support is not available on all product families.  Please
//  refer to the product family datasheet for more information if this feature
//  is available on the target processor.
//#define USB_TRANSCEIVER_OPTION USB_EXTERNAL_TRANSCEIVER

#define USB_SPEED_OPTION USB_FULL_SPEED
//#define USB_SPEED_OPTION USB_LOW_SPEED //(not valid option for PIC24F devices)


#define USB_DEVICE_HID_IDLE_RATE_CALLBACK APP_DeviceMouseIdleRateCallback

//------------------------------------------------------------------------------------------------------------------
//Option to enable auto-arming of the status stage of control transfers, if no
//"progress" has been made for the USB_STATUS_STAGE_TIMEOUT value.
//If progress is made (any successful transactions completing on EP0 IN or OUT)
//the timeout counter gets reset to the USB_STATUS_STAGE_TIMEOUT value.
//
//During normal control transfer processing, the USB stack or the application 
//firmware will call USBCtrlEPAllowStatusStage() as soon as the firmware is finished
//processing the control transfer.  Therefore, the status stage completes as 
//quickly as is physically possible.  The USB_ENABLE_STATUS_STAGE_TIMEOUTS 
//feature, and the USB_STATUS_STAGE_TIMEOUT value are only relevant, when:
//1.  The application uses the USBDeferStatusStage() API function, but never calls
//      USBCtrlEPAllowStatusStage().  Or:
//2.  The application uses host to device (OUT) control transfers with data stage,
//      and some abnormal error occurs, where the host might try to abort the control
//      transfer, before it has sent all of the data it claimed it was going to send.
//
//If the application firmware never uses the USBDeferStatusStage() API function,
//and it never uses host to device control transfers with data stage, then
//it is not required to enable the USB_ENABLE_STATUS_STAGE_TIMEOUTS feature.

#define USB_ENABLE_STATUS_STAGE_TIMEOUTS    //Comment this out to disable this feature.  

//Section 9.2.6 of the USB 2.0 specifications indicate that:
//1.  Control transfers with no data stage: Status stage must complete within 
//      50ms of the start of the control transfer.
//2.  Control transfers with (IN) data stage: Status stage must complete within 
//      50ms of sending the last IN data packet in fullfilment of the data stage.
//3.  Control transfers with (OUT) data stage: No specific status stage timing
//      requirement.  However, the total time of the entire control transfer (ex:
//      including the OUT data stage and IN status stage) must not exceed 5 seconds.
//
//Therefore, if the USB_ENABLE_STATUS_STAGE_TIMEOUTS feature is used, it is suggested
//to set the USB_STATUS_STAGE_TIMEOUT value to timeout in less than 50ms.  If the
//USB_ENABLE_STATUS_STAGE_TIMEOUTS feature is not enabled, then the USB_STATUS_STAGE_TIMEOUT
//parameter is not relevant.

#define USB_STATUS_STAGE_TIMEOUT     (uint8_t)45   //Approximate timeout in milliseconds, except when
                                                //USB_POLLING mode is used, and USBDeviceTasks() is called at < 1kHz
                                                //In this special case, the timeout becomes approximately:
//Timeout(in milliseconds) = ((1000 * (USB_STATUS_STAGE_TIMEOUT - 1)) / (USBDeviceTasks() polling frequency in Hz))
//------------------------------------------------------------------------------------------------------------------

#define USB_SUPPORT_DEVICE

#define USB_NUM_STRING_DESCRIPTORS 3

//#define USB_INTERRUPT_LEGACY_CALLBACKS
#define USB_ENABLE_ALL_HANDLERS
//#define USB_ENABLE_SUSPEND_HANDLER
//#define USB_ENABLE_WAKEUP_FROM_SUSPEND_HANDLER
//#define USB_ENABLE_SOF_HANDLER
//#define USB_ENABLE_ERROR_HANDLER
//#define USB_ENABLE_OTHER_REQUEST_HANDLER
//#define USB_ENABLE_SET_DESCRIPTOR_HANDLER
//#define USB_ENABLE_INIT_EP_HANDLER
//#define USB_ENABLE_EP0_DATA_HANDLER
//#define USB_ENABLE_TRANSFER_COMPLETE_HANDLER

/** DEVICE CLASS USAGE *********************************************/
#define USB_USE_AUDIO_CLASS

#define AUDIO_CONTROL_INTERFACE_ID 0x00
#define AUDIO_STREAMING_INTERFACE_ID 0x01

/************** Entity ID ***********/
#define ID_INPUT_TERMINAL  0x01
#define ID_OUTPUT_TERMINAL 0x02
#define ID_MIXER_UNIT      0x03
#define ID_SELECTOR_UNIT   0x04
#define ID_FEATURE_UNIT    0x05
#define ID_PROCESSING_UNIT 0x06
#define ID_EXTENSION_UNIT  0x07


//Uncomment below handlers if your device supports any of them
/******* Audio Control Request Handlers**********************/
//#define USB_AUDIO_INPUT_TERMINAL_CONTROL_REQUESTS_HANDLER UsbAudioInputTerminalControlRequestsHandler
//#define USB_AUDIO_OUTPUT_TERMINAL_CONTROL_REQUESTS_HANDLER  UsbAudioOutputTerminalControlRequestsHandler
//#define USB_AUDIO_MIXER_UNIT_CONTROL_REQUESTS_HANDLER UsbAudioMixerUnitControlRequestsHandler
//#define USB_AUDIO_SELECTOR_UNIT_CONTROL_REQUESTS_HANDLER UsbAudioSelectorUnitControlRequestsHabdler
//#define USB_AUDIO_FEATURE_UNIT_CONTROL_REQUESTS_HANDLER UsbAudioFeatureUnitControlRequestsHandler
//#define USB_AUDIO_PROCESSING_UNIT_CONTROL_REQUESTS_HANDLER UsbAudioProcessingUnitControlRequestsHandler
//#define USB_AUDIO_EXTENSION_UNIT_CONTROL_REQUESTS_HANDLER  UsbAudioExtensionUnitControlRequestsHandler

/******* Audio Streaming Request Handlers**********************/
//#define USB_AUDIO_INTRFACE_CONTROL_REQUESTS_HANDLER UsbAudioInterfaceControlRequestsHandler
//#define USB_AUDIO_ENDPOINT_CONTROL_REQUESTS_HANDLER UsbAudioEndpointControlRequestsHandler

/******* Additional Request Handlers**********************/
//#define USB_AUDIO_MEMORY_REQUESTS_HANDLER UsbAudioMemoryRequestsHandler
//#define USB_AUDIO_STATUS_REQUESTS_HANDLER UsbAudioStatusRequestsHandler

/** ENDPOINTS ALLOCATION *******************************************/
#define USB_DEVICE_MICROPHONE_DEMO_ENDPOINT             1

/**** MICRPHONE BITS/SAMPLE *****************************************/
#define NO_OF_BYTES_TRANSFRED_IN_A_USB_FRAME 16
// So the NO_OF_BYTES_TRANSFRED_IN_A_USB_FRAME = (No of Samples/milli second  *  No. of bits/ Sample * No of Channels )/8
// The above equation goes true if 'bInterval' is 0x01.

/** DEFINITIONS ****************************************************/

#endif //USBCFG_H