/* 
 * This is an auto-generated file based on the 
 * configuration of the XBee Programmable project.
 * 
 * Do not edit this file.
 */

#ifndef __XBEE_CONFIG_H_
#define __XBEE_CONFIG_H_

/* Project definitions */
#define APP_VERSION_STRING              "Transmitter"
#define CONFIG_XBEE_DIGI_MESH
#define CONFIG_XBEE_SMT
#define CONFIG_XBEE_S8
#define CONFIG_XBEE_FLASH_LEN           32

/* system0 component */
#define SYS_CFG_CLK_48_MHz
#define SYS_CFG_BUSCLK_SYSCLK_DIV2
#define ENABLE_WD
#define WD_CFG_LONG_TOUT

/* special0 component */
#define ENABLE_ASSOCIATION_LED_XPIN_28
#define ENABLE_COMMISSIONING_XPIN_33
#define ENABLE_RESET_PIN_XPIN_6
#define ENABLE_BKGD_PIN_XPIN_9
#define ENABLE_RSSI_PWM_XPIN_7

/* rtc0 component */
#define ENABLE_RTC

/* network0 component */
#define ENABLE_XBEE_HANDLE_TX_STATUS_FRAMES
#define ENABLE_XBEE_HANDLE_ND_RESPONSE_FRAMES

/* uart0 component */
#define ENABLE_UART
#define UART_CFG_MODE_2W                1
#define UART_CFG_BAUDRATE               115200
#define UART_CFG_PAR_EN                 UART_CFG_PARITY_DIS
#define UART_CFG_PAR_VAL                UART_CFG_PARITY_ODD
#define UART_CFG_BITS                   UART_CFG_BITS_8
#define UART_CFG_RX_WATERMARK           1
#define UART_CFG_RX_BUF_LEN             32
#define ENABLE_STDIO_PRINTF_SCANF       1

/* XPIN_1_WIRE_BUS component */
#define ENABLE_ONE_WIRE
#define XPIN_1_WIRE_BUS                 XPIN_5
#define ENABLE_GPIO_XPIN_5
#define GPIO_CFG_DIR_5                  GPIO_CFG_OUTPUT
#define GPIO_CFG_PULL_UP_EN_5           GPIO_CFG_PULL_UP_EN
#define GPIO_CFG_SLEW_RATE_EN_5         GPIO_CFG_SLEW_RATE_EN
#define GPIO_CFG_DRV_STR_5              GPIO_CFG_DRV_STR_LOW

/* Used pins macros */
#define XPIN_28_USED
#define XPIN_33_USED
#define XPIN_6_USED
#define XPIN_9_USED
#define XPIN_7_USED
#define XPIN_4_USED
#define XPIN_3_USED
#define XPIN_5_USED


/* Components includes */
#include <custom.h>
#include <system.h>
#include <rtc.h>
#include <pan_init.h>
#include "xbee/discovery.h"
#include "xbee/wpan.h"
#include "xbee/atcmd.h"
#include <uart.h>
#include <one_wire.h>
#include <gpios.h>

#endif /* __XBEE_CONFIG_H_ */
