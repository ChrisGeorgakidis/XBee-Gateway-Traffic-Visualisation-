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
#include <types.h>

#define NODE_TABLE_SIZE 20

// *** GLOBAL VARIABLES *** //
xbee_node_id_t node_table[NODE_TABLE_SIZE] = {{{{0}}}};

// *** Function Prototypes *** //
xbee_node_id_t *node_add(const xbee_node_id_t *node_id);
xbee_node_id_t *node_by_addr(const addr64 FAR *ieee_be);

#ifdef ENABLE_XBEE_HANDLE_RX
// *** xbee_transparent_rx *** //
// This function is called every time the GATEWAY receives a message. It just //
// dumps the arrived message to the serial console.							  //
int xbee_transparent_rx(const wpan_envelope_t FAR *envelope, void FAR *context)
{
    xbee_node_id_t *node_id;
	char out[ADDR64_STRING_LENGTH];	
	const uint16_t FAR *data = envelope->payload;

	printf("Data from ");
	node_id = node_by_addr(&envelope->ieee_address);
	if (node_id != NULL)
	{
		printf("'%s': ", node_id->node_info);
	}
	else
	{
		printf("'%s': ", addr64_format(out, &envelope->ieee_address));
	}
	printf("0x%x\n", *data);

	return 0;
}
#endif

#ifdef ENABLE_XBEE_HANDLE_ND_RESPONSE_FRAMES
// *** node_discovery_callback *** //
// This function is called every time a node is discovered, either by receiving   //
// a NodeIF message or because a node search was started with function xbee_disc_ //
// discover_nodes() //
void node_discovery_callback(xbee_dev_t *xbee, const xbee_node_id_t *node_id)
{
	// Add node into the node table //
	node_add(node_id);

	// DEbugging function used to dymp an xbee_node_id_t structure to stdout //
	xbee_disc_node_id_dump(node_id);

	return;
}
#endif


void main(void)
{
	sys_hw_init();
	sys_xbee_init();
	sys_app_banner();

	for (;;) {
		/* Write your code here... */
		sys_watchdog_reset();
		sys_xbee_tick();
	}
}

// *** node_add *** //
// Copy node_id into the node table, possibly updating existing entry //
xbee_node_id_t *node_add(const xbee_node_id_t *node_id)
{
	uint16_t i;
	uint_node_id_t *curr, *copy = NULL;

	for (i = 0; i < NODE_TABLE_SIZE; i++)
	{
		curr = &node_table[i];
		if (addr64_equal(&node_id->ieee_addr_be, &curr->ieee_addr_be))
		{
			// Node with node_id is already in the node table //
			copy = curr;
			break;
		}

		if (copy == NULL && addr64_is_zero(&curr->ieee_addr_be))
		{
			// Node is not in the node table. So it must be added at the end of it //
			copy = curr;
		}
	}
	
	if (copy != NULL)
	{
		// Insert or update the id of the current node //
		*copy = *node_id;
	}

	return copy;
}

xbee_node_id_t node_by_addr(const addr64 FAR *ieee_be)
{
	uint16_t i;
	xbee_node_id_t *curr;

	for (i = 0; i < NODE_TABLE_SIZE; i++)
	{
		curr = node_table + i;
		if (addr64_equal(ieee_be, &curr->ieee_addr_be))
		{
			return curr;
		}
	}
}