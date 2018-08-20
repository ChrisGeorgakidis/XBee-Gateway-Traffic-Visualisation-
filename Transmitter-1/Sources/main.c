/***** XBEE APPLICATION PROJECT *****
 * 
 * Auto-generated header with information about the 
 * relation between the XBee module pins and the 
 * project components.
 * 
 ************ XBEE LAYOUT ***********
 * 
 * This layout represents the XBee 865/868LP DigiMesh (S8) module 
 * selected for the project with its pin distribution:
 *            ________________________
 *           |                        |- XPIN37
 *           |                ____    |- XPIN36
 *           |              //    \\  |- XPIN35
 *   XPIN1  -|             ||      || |- XPIN34
 *   XPIN2  -|              \\____//  |- XPIN33
 *   XPIN3  -|                        |- XPIN32
 *   XPIN4  -| =====================  |- XPIN31
 *   XPIN5  -| #   # ####  #### ####  |- XPIN30
 *   XPIN6  -|  # #  #   # #    #     |- XPIN29
 *   XPIN7  -|   #   ####  ###  ###   |- XPIN28
 *   XPIN8  -|  # #  #   # #    #     |- XPIN27
 *   XPIN9  -| #   # ####  #### ####  |- XPIN26
 *   XPIN10 -| =====================  |- XPIN25
 *   XPIN11 -|                        |- XPIN24
 *   XPIN12 -|                        |- XPIN23
 *   XPIN13 -|                        |- XPIN22
 *           |________________________|
 *             |  |  |  |  |  |  |  |
 *             |  |  |  |  |  |  |  XPIN21
 *             |  |  |  |  |  |  XPIN20
 *             |  |  |  |  |  XPIN19
 *             |  |  |  |  XPIN18
 *             |  |  |  XPIN17
 *             |  |  XPIN16
 *             |  XPIN15
 *             XPIN14
 * 
 ************ PINS LEGEND ***********
 * 
 * The following list displays all the XBee Module pins 
 * with the project component which is using each one:
 * 
 *   XPIN1 = GND
 *   XPIN2 = VCC
 *   XPIN3 = uart0 [TX Pin]
 *   XPIN4 = uart0 [RX Pin]
 *   XPIN5 = <<UNUSED>>
 *   XPIN6 = special0 [Reset Pin]
 *   XPIN7 = special0 [RSSI PWM Pin]
 *   XPIN8 = <<UNUSED>>
 *   XPIN9 = special0 [BKGD Pin]
 *   XPIN10 = <<UNUSED>>
 *   XPIN11 = GND
 *   XPIN12 = <<UNUSED>>
 *   XPIN13 = GND
 *   XPIN14 = <<UNUSED>>
 *   XPIN15 = <<UNUSED>>
 *   XPIN16 = <<UNUSED>>
 *   XPIN17 = <<UNUSED>>
 *   XPIN18 = <<UNUSED>>
 *   XPIN19 = <<UNUSED>>
 *   XPIN20 = <<UNUSED>>
 *   XPIN21 = Do not Connect
 *   XPIN22 = GND
 *   XPIN23 = Do not Connect
 *   XPIN24 = <<UNUSED>>
 *   XPIN25 = <<UNUSED>>
 *   XPIN26 = <<UNUSED>>
 *   XPIN27 = VCC REF
 *   XPIN28 = special0 [Association Pin]
 *   XPIN29 = <<UNUSED>>
 *   XPIN30 = <<UNUSED>>
 *   XPIN31 = <<UNUSED>>
 *   XPIN32 = <<UNUSED>>
 *   XPIN33 = special0 [Commissioning Pin]
 *   XPIN34 = Do not Connect
 *   XPIN35 = GND
 *   XPIN36 = <<UNUSED>>
 *   XPIN37 = Do not Connect
 *
 ************************************/

#include <xbee_config.h>
#include <xbee/transparent_serial.h>
#include <xbee/byteorder.h>
#include <types.h>
#include <string.h>

#define TARGET_NI "GATEWAY"

// *** GLOBAL VARIABLES *** //
addr64 gateway_ieeeaddr; // 64-bit address of the gateway //
bool_t node_discovery_in_progress = FALSE; // Flag that indicates whether node //
										  // discovery is in progress or not. //				 
wpan_envelope_t envelope;
uint16_t counter;

/* Timer signaled a new sample has to be taken */
bool_t app_request_send = FALSE;

// *** EVENT HANDLERS *** //

#ifdef ENABLE_XBEE_HANDLE_ND_RESPONSE_FRAMES
void node_discovery_callback(xbee_dev_t *xbee, const xbee_node_id_t *node_id)
{
	/* This function is called every time a node is discovered, either by
	 * receiving a NodeID message or because a node search was started with
	 * function xbee_disc_discover_nodes() */
	
	if (node_id == NULL)
	{
		printf("Node Discovery timed out!\n\n");
		node_discovery_in_progress = FALSE;
		return;
	}

	if (strncmp(node_id->node_info, TARGET_NI, strlen(TARGET_NI)) == 0)
	{
		char address[ADDR64_STRING_LENGTH];

		memcpy(&gateway_ieeeaddr, &node_id->ieee_addr_be, sizeof(gateway_ieeeaddr));
		printf("GATEWAY: %s\n", addr64_format(address, &gateway_ieeeaddr));

		// Starting with a black envelope, fill in the device, the 64-bit IEEE //
		// address and the 16-bit network address of the destination.          //
		wpan_envelope_create(&envelope, &xdev.wpan_dev, &gateway_ieeeaddr, WPAN_NET_ADDR_UNDEFINED);

		node_discovery_in_progress = FALSE;

	}
	
	return;
}
#endif

#ifdef ENABLE_XBEE_HANDLE_TX_STATUS_FRAMES
int xbee_transmit_status_handler(xbee_dev_t *xbee, const void FAR *payload,
								 uint16_t length, void FAR *context)
{
	const xbee_frame_transmit_status_t FAR *frame = payload;

	/* it may be necessary to push information up to user code so they know when
	 * a packet has been received or if it didn't make it out.
	 */
	printf("TransmitStatus: id 0x%02x retries=%d del=0x%02x disc=0x%02x\n",
		   frame->frame_id,
		   frame->retries, frame->delivery,
		   frame->discovery);

	return 0;
}
#endif

#if defined(RTC_ENABLE_PERIODIC_TASK)
void rtc_periodic_task(void)
{
	/*
     * Function call every RTC_CFG_PERIODIC_TASK_PERIOD * 8 ms.
     * This function is called from the timer ISR, please be brief
     * and exit, or just set a flag and do your home work in the 
     * main loop
     */

	app_request_send = TRUE;
}
#endif

// *** FUNCTIONS *** //

// ***node_discovery*** //
// Discovers for the gateway node if it is not already discovered //
void node_discovery()
{
	if (node_discovery_in_progress == FALSE && addr64_is_zero(&gateway_ieeeaddr))
	{
		printf("GATEWAY not yet discovered. Sending DiscoverNode...\n");
		xbee_disc_discover_nodes(&xdev, TARGET_NI);
		node_discovery_in_progress = TRUE;
	}
}

// ***data_generation*** //
// Generates the data that will be transmitted lated to the gateway.  //
// In this project the device receives data from the DHT22 sensor and //
// send them to the GATEWAY. In other words, the device sends the     //
// current humidity and temperature to the the GATEWAY.               //
bool_t data_generation()
{

	counter = counter + 1;

	sys_watchdog_reset();
	
	return (TRUE);
}

// ***data_transmission*** //
// Sends the data received by the DHT22 sensor to the GATEWAY.  //
// In order to do this, it packages the data inside an envelope //
// created for the GATEWAY.                                     //
void data_transmission()
{
	int successful_transmission = 1;

	char txbuf[1024];
	sprintf(txbuf, "Counter: %d", counter);

	printf("%s\n", txbuf);

	successful_transmission = xbee_transparent_serial_str(&envelope, txbuf);

	
	if (successful_transmission == -EINVAL)
	{
		printf("Txbuf not sent! (EINVAL)\n");
	}
	else if (successful_transmission == -EMSGSIZE)
	{
		printf("Txbuf too big to be sent!\n");
	}
	else if (successful_transmission == 0)
	{
		printf("Txbuf successfully sent!\n");
	}
	else
	{
		printf("Txbuf not sent!\n");
	}
}

void main(void)
{
	sys_hw_init();
	sys_xbee_init();
	sys_app_banner();

#ifdef XBEE_ATCMD_PARAM_NI
	printf("Starting using NI = %s\n", XBEE_ATCMD_PARAM_NI);
#else
	printf("NI parameter not configured. You should configure it!!!.\n");
#endif

	for (;;)
	{
		if (app_request_send == TRUE)
		{
			app_request_send = FALSE;

			node_discovery();
			if (addr64_is_zero(&gateway_ieeeaddr))
			{
				printf("GATEWAY not discovered yet!");
			}
			else
			{
				if (data_generation() == FALSE)
				{
					printf("Data are not sent!\n");
				}
				else
				{
					sys_watchdog_reset();
					data_transmission();
				}
			}
		}
		

		sys_watchdog_reset();
		sys_xbee_tick();
	}
}
