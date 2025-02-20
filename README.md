# fortiscript-py
Converts CSV formated firewall object data into Fortinet firewall configuration scripts

You must normalize the object data in CSV format with the following schema:  
**Name, ipv4_address, mask, comment**

  **Name:** Maximum 79 characters, Invalid characters: < > ( ) # ' "  
  **ipv4_address:** Single IP or IP Range, (eg. 1.2.3.4 or 1.1.1.1 - 1.1.2.1)  
  **mask:** Optional field containing subnet mask. Not required for IP range objects. If null then mask will be hard coded as 255.255.255.255 (/32)  
  **comment:** Optional free text field. If null then no comment will be added to the output. Commas in comments will cause the message to be truncated. All comments truncated to 255 characters maximum.  

Coming soon: Service Objects, Domain (FQDN) Objects, and Group objects support  
Coming who knows when: firewall policy rule script generation
