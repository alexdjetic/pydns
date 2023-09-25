import dns.query
import dns.message
import dns.rdatatype
import dns.resolver
import socket
import threading
import time

# DNS server configuration
DNS_SERVER_IP = '0.0.0.0'  # Listen on all available network interfaces
DNS_SERVER_PORT = 53
DNS_ZONE = {}
FORWARDER_IP = '8.8.8.8'
TTL = 300
DYNAMIC_DNS_RECORDS = {}

def dns_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((DNS_SERVER_IP, DNS_SERVER_PORT))
    print(f'DNS server listening on {DNS_SERVER_IP}:{DNS_SERVER_PORT}')

    while True:
        data, addr = udp_socket.recvfrom(1024)
        response = handle_dns_query(data)
        udp_socket.sendto(response.to_wire(), addr)

def handle_dns_query(query_data):
    query = dns.message.from_wire(query_data)
    response = dns.message.make_response(query)
    
    for question in query.question:
        qname = question.name.to_text().lower()
        
        if qname in DYNAMIC_DNS_RECORDS:
            # If the domain is in the dynamic DNS records, respond with the associated IP
            response.answer.append(
                dns.rrset.from_text(
                    question.name, TTL, dns.rdataclass.IN, dns.rdatatype.A,
                    DYNAMIC_DNS_RECORDS[qname]
                )
            )
        elif qname in DNS_ZONE:
            # If the domain is in the static DNS zone, respond with the local IP
            response.answer.append(
                dns.rrset.from_text(
                    question.name, TTL, dns.rdataclass.IN, dns.rdatatype.A,
                    DNS_ZONE[qname]
                )
            )
        else:
            # If the domain is not found, use a forwarder (8.8.8.8) to resolve
            forwarder = dns.resolver.Resolver()
            forwarder.nameservers = [FORWARDER_IP]
            
            try:
                forward_response = forwarder.query(question.name, question.rdtype)
                for rr in forward_response:
                    response.answer.append(rr)
            except dns.exception.DNSException:
                pass
    
    return response

def update_dynamic_dns_record(domain, ip):
    DYNAMIC_DNS_RECORDS.setdefault(domain, ip)

if __name__ == "__main__":
    dns_server_thread = threading.Thread(target=dns_server)
    dns_server_thread.daemon = True
    dns_server_thread.start()
