#include <arpa/inet.h> // inet_addr

#include <cstring>     // memcpy

#include <iostream>

#include <netinet/ether.h> // ethernet header struct

#include <netinet/ip.h>    // ip header struct

#include <netinet/udp.h>   // udp header struct

#include <pcap.h>          // pcap libary

#include <unistd.h>
#include <cmath>
#include <vector>



#define MAX_PACKET_SIZE 65535



/* some useful identifiers:

 * - ETH_ALEN = 6   (ethernet address length)

 * - ETH_HLEN = 14	(ethernet header length)

*/



using namespace std;



// TODO 5

void modify_mac_address(struct ether_header *eth_header, const char* new_src_str, const char* new_dst_str) {

    // struct ether_header reference:

    // https://sites.uclouvain.be/SystInfo/usr/include/net/ethernet.h.html

	// Convert MAC addresses from string to binary
    struct ether_addr  new_src, new_dst;
    ether_aton_r(new_src_str, &new_src);
    ether_aton_r(new_dst_str, &new_dst);

    // modify source MAC address
    memcpy(eth_header->ether_shost, &new_src, ETH_ALEN);
    
    // Check and modify destination MAC address
    memcpy(eth_header->ether_dhost, &new_dst, ETH_ALEN);

    cout << "MAC src and dst address modified successfully\n"; 

}



// TODO 6

void modify_ip_address(struct ip *ip_header, const char* new_src_str, const char* new_dst_str) {

    if (inet_pton(AF_INET, new_src_str, &(ip_header->ip_src)) == 1) {
    	cout << "ip_src modified" << '\n';
    }
    
    if (inet_pton(AF_INET, new_dst_str, &(ip_header->ip_dst)) == 1) {
    	cout << "ip_dst modified" << '\n';
    }

}

useconds_t calTime(timeval lst_timestamp, timeval timestamp) {
	// visualised timestamp
	cout << "last timestamp: " << lst_timestamp.tv_sec << "+" << lst_timestamp.tv_usec << "us\n";
	cout << "this timestamp: " << timestamp.tv_sec << "+" << timestamp.tv_usec << "us\n";
	
	useconds_t timediff;
	timediff += (timestamp.tv_sec - lst_timestamp.tv_sec) * 1000000;
	
	double udiff = (double)(timestamp.tv_usec - lst_timestamp.tv_usec) / 1000000.0; //to be sec
	udiff = round(udiff *10.0) / 10.0;
	timediff += (int)udiff*1000000;
	
	return timediff;
}

int main() {

	cerr << "start" << "\n\n";

    char errbuf[PCAP_ERRBUF_SIZE];

    // TODO 1: Open the pcap file

    pcap_t* handle_pcap = pcap_open_offline("./test.pcap", errbuf);

  	if (handle_pcap == NULL) {

		cerr << "Error opening pcap file: " << errbuf << endl;

		pcap_close(handle_pcap);

		return 1;

	}

  

    // TODO 2: Open session with loopback interface "lo"

    pcap_t* handle_lo = pcap_open_live("lo", BUFSIZ, 1, 1000, errbuf);

	if (handle_lo == NULL) {

		cerr << "Error opening live capture: " << errbuf << endl;

		pcap_close(handle_pcap);

		return 2;

	}



    struct pcap_pkthdr *header;

    const u_char *packet;


    // TODO 8: Variables to store the time difference between each packet
	timeval lst_timestamp = {0, 0};
	vector<double> rec;
	

    // TODO 3: Loop through each packet in the pcap file
    while (pcap_next_ex(handle_pcap, &header, &packet) == 1) {

        // TODO 4: Send the original packet
        /* // Comment for modified part task
        

		if (pcap_inject(handle_lo, packet, header->len) == -1) {

			cerr << "injection wrong" << errbuf << endl;

			pcap_close(handle_pcap);

			pcap_close(handle_lo);

			return 4;

		}
		
		*/
		

		

		// TODO 5: Modify mac address (function up above)

        struct ether_header *eth_header = (struct ether_header *)packet; //copy packet to eth_header

        modify_mac_address(eth_header, "08:00:12:34:56:78", "08:00:12:34:ac:c2");


		// TODO 6: Modify ip address if it is a IP packet (hint: ether_type)
        if (ntohs(eth_header->ether_type) == ETHERTYPE_IP) {
        	cout << "IPv4 pkt checked" << '\n'; 
            // Assuming Ethernet headers
            struct ip *ip_header = (struct ip *)(packet + ETH_HLEN); //point to part
            modify_ip_address(ip_header, "10.1.1.3", "10.1.1.4");   // modify function up above
        }
        
        // TODO 8: Calculate the time difference between the current and the
        // previous packet and sleep. (hint: usleep)
        timeval timestamp = header->ts; // get the timestamp
       
        
        if (lst_timestamp.tv_sec != 0 && lst_timestamp.tv_sec != 0) {
        	useconds_t timediff = calTime(lst_timestamp, timestamp);
        	usleep(timediff);
        	cout << "sleep " << timediff << '\n';	
        	rec.push_back(timediff/1000000.0); // second format
        }
        
        // TODO 8: Update the previous packet time
        lst_timestamp = timestamp;
        
        // TODO 7: Send the modified packet
        if (pcap_inject(handle_lo, packet, header->len) == -1) {

			cerr << "injection wrong" << errbuf << endl;

			pcap_close(handle_pcap);

			pcap_close(handle_lo);

			return 4;

		}
		else cout << "injected modified pkt successfully" << "\n\n";
		

    }



    // Close the pcap file

    pcap_close(handle_pcap);

    pcap_close(handle_lo);

    cout << "end" << endl;
    
    // Print the timestamp difference
    cout << "TimeDiff: ";
    for (auto e: rec) cout << e << " ";
    cout << "\n";
    

    return 0;

}