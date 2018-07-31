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
 *   XPIN5 = XPIN_1_WIRE_BUS [1-Wire Bus pin]
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
#include <dht.h>

#define TARGET_NI "TARGET"

// *** GLOBAL VARIABLES *** //
addr64 gateway_ieeeaddr; // 64-bit address of the gateway device //
bool_t node_discovery_in_progress; // Signal that indicates whether node //
								   // discovery is in progress or not.   //
uint16_t humidity;
int16_t temperature;
char humid_buf[sizeof(uint16_t) + 1];
char temp_buf[sizeof(int16_t) + 1];
wpan_envelope_t envelope;

// *** FUNCTION PROTOTYPES *** //
void node_discovery();
bool_t data_generation();
void data_transmission();

#ifdef ENABLE_XBEE_HANDLE_ND_RESPONSE_FRAMES
void node_discovery_callback(xbee_dev_t *xbee, const xbee_node_id_t *node_id)
{
	/* This function is called every time a node is discovered, either by
	 * receiving a NodeID message or because a node search was started with
	 * function xbee_disc_discover_nodes() */

	if (node_id == NULL)
	{
		printf("Node Discovery timed out!\n");
	}

	if (strncmp(node_id->node_info, TARGET_NI, strlen(TARGET_NI)) == 0)
	{
		char address[ADDR64_STRING_LENGTH];

		memcpy(&gateway_ieeeaddr, &node_id->ieee_addr_be, sizeof(gateway_ieeeaddr));
		printf("GATEWAY: %s\n", addr64_format(address, &gateway_ieeeaddr));

		// Starting with a blank envelope, fill in the device, the 64-bit IEEE //
		// address and the 16-bit network address of the destination.          //
		wpan_envelope_create(&envelope, &xdev.wpan_dev, &gateway_ieeeaddr, WPAN_NET_ADDR_UNDEFINED);

		// Simple interface for sending a command with a parameter to the local XBee //
		// without checking for a response.                                          //
		// Simulate Commissioning Button press so a Node Identification broadcast    //
		// transmission is queued to be sent at the begging of the next network wake //
		// cycle. This way the GATEWAY will know our NI.							 //
		(void)xbee_cmd_simple(&xdev, "CB", 1);
	}

	node_discovery_in_progress = FALSE; 

	return;
}
#endif


#ifdef ENABLE_XBEE_HANDLE_TX_STATUS_FRAMES
int xbee_transmit_status_handler(xbee_dev_t *xbee, const void FAR *payload,
                                 uint16_t length, void FAR *context)
{
    const xbee_frame_transmit_status_t FAR *frame = payload;

	printf("Transmission Status: id = 0x%02x retries = %d del = 0x%02x disc = 0x%02x\n",
			frame->frame_id, frame->retries, frame->delivery, frame->discovery);
    return 0;
}
#endif

void main(void)
{
	sys_hw_init();
	sys_xbee_init();
	sys_app_banner();

	node_discovery();
	while (node_discovery_in_progress); // wait until node discovery is done //
	if (addr64_is_zero(&gateway_ieeeaddr))
	{
		printf("GATEWAY not discovered yet. Sample lost.\n");
	}
	else
	{
		sys_watchdog_reset();
		if (data_generation())
		{
			printf("Data are not sent!\n");
		}
		else
		{
			data_transmission();
		}

	}


	for (;;) {
		/* Write your code here... */
		sys_watchdog_reset();
		sys_xbee_tick();
	}
}

// *** node_discovery *** //
// Discovers for the gateway node if it is not already discovered //
void node_discovery()
{
	if(!node_discovery_in_progress && addr64_is_zero(&gateway_ieeeaddr))
	{
		printf("GATEWAY not discovered yet. Sending DiscoverNode\n");
		xbee_disc_discover_nodes(&xdev, TARGET_NI);
		node_discovery_in_progress = TRUE;
	}
	else if (node_discovery_in_progress)
	{
		printf("Node discovery in progress.\n");
	}
	else
	{
		printf("GATEWAY already discovered.\n");
	}
}

// *** data_generation *** //
// Generates the data that will be transmitted lated to the gateway //
// In this project the device take the data that DHT22 sensor sends //
// to it. In other words the device sends the current humidity and  //
// temperature to the gateway.                                      //
bool_t data_generation()
{
	ssize_t ret;
	uint8_t rom_search[8];
	uint8_t *rom;
	uint8_t rxbuf[5];
	ssize_t i;

	// Starts the communication between the xbee and the DHT22 sensor. //
	ret = dht_init_communication();
	ret = dht_read_data(rxbuf);
	sys_watchdog_reset();
	printf("\nCommunication Initialisation:\t[OK]\n");
	printf("Data Transmission:\t[OK]\n");

	if (ret == 0)
	{
		ret = dht_checksum(rxbuf, &humidity, &temperature);
		if (ret)
		{
			printf("Check Data:\t[OK]\n");
			return (TRUE);
		}
		else
		{
			printf("Check Data:\t[ERROR]\n");
			printf("\t INFO	: Parity Error\n");
			return (FALSE);
		}
	}
}

// *** data_transmission *** //
// Sends the data received by the DHT22 sensor to the GATEWAY.  //
// In order to do this, it packages the data inside an envelope //
// created for the GATEWAY.                                     //
void data_transmission()
{
	int successful_transmission = 1;
	uint8_t tries = 0;

	printf("Sending humidity: 0x%x\n", humidity);

	// Store the data into the transmission buffer // 
	*(uint16_t *)humid_buf = humidity;
	// Store the transmission data into the envelope //
	envelope.payload = humid_buf;
	envelope.length = sizeof(humid_buf);

	
	successful_transmission = xbee_transparent_serial(&envelope);
	
	// Check if the data has been sent  successfully. If there was a problem //
	// sending the data, then try again to resend it. The program stops      //
	// trying sending the data after 10 tries and continues with the next    //
	// data.																 //
	if (successful_transmission == 0) // Data sent successfully //
	{
		printf("-> -> Sample sent!\n");
	}
	else	// Data didn't send //
	{
		printf("ERROR: Humidity didn't send!\n Trying to resend the humidity...\n");
		while (successful_transmission != 0 || tries <= 10)
		{
			tries++;
			successful_transmission = xbee_transparent_serial(&envelope);
		}
		printf("INFO: The humidity was sent 10 times unsuccessfully!\n Continue  with next data...\n");
	}

	printf("Sending temperature: 0x%x\n", temperature);

	// Store the data into the transmission buffer //
	*(uint16_t *)temp_buf = temperature;
	// Store the transmission data into the envelope //
	envelope.payload = temp_buf;
	envelope.length = sizeof(temp_buf);


	successful_transmission = xbee_transparent_serial(&envelope);

	// Check if the data has been sent  successfully. If there was a problem //
	// sending the data, then try again to resend it. The program stops      //
	// trying sending the data after 10 tries and continues with the next    //
	// data.																 //
	if (successful_transmission == 0) // Data sent successfully //
	{
		printf("-> -> Sample sent!\n");
	}
	else // Data didn't send //
	{
		printf("ERROR: Temperature didn't send!\n Trying to resend the temperature...\n");
		while (successful_transmission != 0 || tries <= 10)
		{
			tries++;
			successful_transmission = xbee_transparent_serial(&envelope);
		}
		printf("INFO: The humidity was sent 10 times unsuccessfully!\n Continue  with next data...\n");
	}
	return;
}
