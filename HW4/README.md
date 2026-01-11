# OSPF (Open Shortest Path First)

---

## What is OSPF?

OSPF (Open Shortest Path First) is a common **dynamic routing protocol** that exchanges routing information among routers to determine the most **efficient and shortest paths**.

- Link-state routing protocol  
- Uses the **Shortest Path First (SPF / Dijkstra)** algorithm  
- Commonly used in **enterprise networks**, campus networks, and ISP internal networks  

---

## Basic Components and Principles (Operation)

### OSPF Message Types

OSPF uses the following message (packet) types to establish neighbor relationships and synchronize routing information:

- **Hello Packet**
  - Discovers and maintains neighbor relationships
  - Builds and maintains the **Neighbor Table**

- **Database Description (DBD) Packet**
  - Exchanges summaries (LSA headers) of the LSDB
  - Used to compare database contents between neighbors

- **Link-State Request (LSR) Packet**
  - Requests specific LSAs that are missing or outdated

- **Link-State Update (LSU) Packet**
  - Carries and floods LSAs to neighbors

- **Link-State Acknowledgment (LSAck) Packet**
  - Confirms receipt of LSAs

> **DBD, LSR, LSU, and LSAck packets are used to synchronize and maintain the LSDB.**

---

### OSPF Databases

OSPF maintains three main databases:

- **Neighbor Table (Adjacency Database)**  
  - Stores information about directly connected neighbors  
  - Built using Hello packets  

- **Link-State Database (LSDB)**  
  - Stores the complete network topology within an area  
  - Built using exchanged LSAs  

- **Routing Table (Forwarding Database)**  
  - Stores the best paths calculated by the SPF algorithm  
  - Used to forward data packets
 
---

### OSPF Router (Neighbor) States

OSPF routers transition through several **neighbor states** while forming adjacencies and synchronizing routing information.
- Down
  - No Hello packets have been received from the neighbor
  - Initial state of the neighbor relationship
  - The neighbor is unknown or unreachable
- Init
  - A Hello packet has been received from the neighbor
  - The router does **not** see its own Router ID in the neighbor’s Hello packet
  - One-way communication is established
- 2-Way
  - Bidirectional communication is established
  - The router sees its own Router ID in the neighbor’s Hello packet
  - The **Neighbor Table** is created
  - DR / BDR election occurs on multi-access networks

> Note: Not all neighbors reach the Full state.  
> On broadcast networks, only DR and BDR form full adjacencies.

- ExStart
  - Routers negotiate **master and slave roles**
  - Initial sequence numbers are agreed upon
  - Preparation for LSDB synchronization
- Exchange
  - Routers exchange **Database Description (DBD) packets**
  - LSDB summaries (LSA headers) are compared
  - Determines which LSAs are missing or outdated
- Loading
  - Routers request missing LSAs using **Link-State Request (LSR) packets**
  - Requested LSAs are sent using **Link-State Update (LSU) packets**
  - LSAs are acknowledged with **Link-State Acknowledgment (LSAck) packets**
- Full
  - LSDBs are fully synchronized
  - Routers have identical LSDBs within the same area
  - The SPF algorithm can be executed to calculate routes
  - Stable and operational state

---

### Neighbor State Transition (Summary)
<details>
  <summary>Click to expand image</summary>
  <img width="1442" height="4502" alt="image" src="https://github.com/user-attachments/assets/fff07b8b-cac9-4389-8162-659204f06178" />
</details>

---
## Utilization
1. Activate the OSPF router with **Router ID = 1**:\
    ```python ospf.py 1```.
2. To __add a link of cost 3__ to the neighbor with _Router ID = 2_:\
    ```addlink 2 3```.
3. To __update the cost of the link__ to the neighbor with _Router ID = 2_ and set its __values to 4__:\
   ```setlink 2 4```.
4. To __remove the link__ to the neighbor with _Router ID = 1_:\
   ```rmlink 1```.
5. To __send a message "hi"__ to the destination router with _Router ID = 3_:\
   ```send 3 hi```
