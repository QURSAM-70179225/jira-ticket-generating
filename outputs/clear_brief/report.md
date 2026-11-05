# Brief → Dev Tasks report

Generated 2026-11-05T07:00:27+00:00 with model `openai/gpt-oss-20b`.

## Client brief (numbered)

- **S1** Sweet Crumbs Bakery wants an online ordering website for its single shop in Lahore.
- **S2** The website is for customers who want to order cakes and pastries for pickup.
- **S3** Customers must be able to browse a menu of products with a name, photo, price and description for each item.
- **S4** Customers must be able to add products to a cart and change the quantity of each item.
- **S5** Customers must choose a pickup date and a pickup time slot when placing an order.
- **S6** Pickup time slots are every 30 minutes between 10:00 AM and 8:00 PM.
- **S7** Payment is cash on pickup only; no online payment is needed.
- **S8** After placing an order, the customer must receive a confirmation email with an order number.
- **S9** The bakery staff need an admin page to view all orders for a selected date.
- **S10** Staff must be able to mark an order as "Ready" or "Collected".
- **S11** Staff must be able to add, edit and remove menu products from the admin page.
- **S12** The website must be available in English only.
- **S13** The menu and ordering pages are the highest priority.
- **S14** The website must go live by 15 December 2026.

## Open questions for the client

- **Q-001** [missing] What customer contact information is required to place an order and receive the confirmation email?  
  Source: S8 "After placing an order, the customer must receive a confirmation email with an order number. (S8)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- **Q-002** [missing] Do customers need to create an account or log in to place an order, or can they order as guests?  
  Source: S2 "The website is for customers who want to order cakes and pastries for pickup. (S2)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- **Q-003** [missing] Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?  
  Source: S9 "The bakery staff need an admin page to view all orders for a selected date. (S9)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- **Q-004** [missing] What is the allowed range of pickup dates that customers can select?  
  Source: S5 "Customers must choose a pickup date and a pickup time slot when placing an order. (S5)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- **Q-005** [missing] Which email service or provider will be used to send the order confirmation emails?  
  Source: S8 "After placing an order, the customer must receive a confirmation email with an order number. (S8)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- **Q-006** [vague] What does "highest priority" mean in terms of development sequencing and feature completion?  
  Source: S13 "The menu and ordering pages are the highest priority. (S13)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- **Q-007** [scope_gap] Will customers be able to view the status of their order on the website after placing it?  
  Source: S8 "After placing an order, the customer must receive a confirmation email with an order number. (S8)" · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011

## Task breakdown


### TASK-001 · Epic: Admin Management
Provide staff interface to manage orders and menu  
Source: S9: "The bakery staff need an admin page to view all orders for a selected date."

- **TASK-002** [Story] Create admin order list view — _Needs clarification_
- **TASK-003** [Story] Implement order status updates — _Needs clarification_
- **TASK-004** [Story] Admin menu CRUD — _Needs clarification_

### TASK-005 · Epic: Menu and Ordering
Menu and ordering pages are the highest priority  
Source: S13: "The menu and ordering pages are the highest priority."

- **TASK-006** [Story] Implement product menu display — _Needs clarification_
- **TASK-007** [Story] Add products to cart and adjust quantity — _Needs clarification_
- **TASK-008** [Story] Select pickup date and time slot — _Needs clarification_
- **TASK-009** [Story] Generate pickup time slots — _Needs clarification_
- **TASK-010** [Story] Handle cash on pickup payment — _Needs clarification_
- **TASK-011** [Story] Send order confirmation email — _Needs clarification_

## Tickets

### TASK-001 — Admin Management

| Field | Value |
|---|---|
| Type | Epic |
| Parent | — |
| Status | Needs clarification (7 open question(s)) |
| Description | Provide staff interface to manage orders and menu |
| Source reference | S9: "The bakery staff need an admin page to view all orders for a selected date." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Epic: see child tickets TASK-002, TASK-003, TASK-004
- Project constraint: The website must be available in English only. [S12]
- Project constraint: The website must go live by 15 December 2026. [S14]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

**Python corrections (AI output not trusted)**

- Constraint S12 was on no task: added as a project constraint ("The website must be available in English only.")
- Constraint S14 was on no task: added as a project constraint ("The website must go live by 15 December 2026.")

### TASK-002 — Create admin order list view

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (7 open question(s)) |
| Description | Show all orders for a selected date |
| Source reference | S9: "The bakery staff need an admin page to view all orders for a selected date" |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- The bakery staff need an admin page to view all orders for a selected date [S9: "The bakery staff need an admin page to view all orders for a selected date"]

**Open questions**

- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-003 — Implement order status updates

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (7 open question(s)) |
| Description | Allow staff to mark orders as "Ready" or "Collected" |
| Source reference | S10: "Staff must be able to mark an order as "Ready" or "Collected"" |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Staff must be able to mark an order as "Ready" or "Collected" [S10: "Staff must be able to mark an order as "Ready" or "Collected""]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-004 — Admin menu CRUD

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (7 open question(s)) |
| Description | Enable staff to add, edit and remove menu products from the admin page |
| Source reference | S11: "Staff must be able to add, edit and remove menu products from the admin page" |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Staff must be able to add, edit and remove menu products from the admin page [S11: "Staff must be able to add, edit and remove menu products from the admin page"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-005 — Menu and Ordering

| Field | Value |
|---|---|
| Type | Epic |
| Parent | — |
| Status | Needs clarification (7 open question(s)) |
| Description | Menu and ordering pages are the highest priority |
| Source reference | S13: "The menu and ordering pages are the highest priority." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Epic: see child tickets TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
- Project constraint: The website must be available in English only. [S12]
- Project constraint: The website must go live by 15 December 2026. [S14]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

**Python corrections (AI output not trusted)**

- Constraint S12 was on no task: added as a project constraint ("The website must be available in English only.")
- Constraint S14 was on no task: added as a project constraint ("The website must go live by 15 December 2026.")

### TASK-006 — Implement product menu display

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-005 |
| Status | Needs clarification (7 open question(s)) |
| Description | Display a menu of products with a name, photo, price and description for each item |
| Source reference | S3: "Customers must be able to browse a menu of products with a name, photo, price and description for each item" |
| Dependencies | None stated in the brief |
| Priority | menu and ordering pages are the highest priority (S13: "The menu and ordering pages are the highest priority") |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Customers must be able to browse a menu of products with a name, photo, price and description for each item [S3: "Customers must be able to browse a menu of products with a name, photo, price and description for each item"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-007 — Add products to cart and adjust quantity

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-005 |
| Status | Needs clarification (7 open question(s)) |
| Description | Allow customers to add products to a cart and change the quantity of each item |
| Source reference | S4: "Customers must be able to add products to a cart and change the quantity of each item" |
| Dependencies | None stated in the brief |
| Priority | menu and ordering pages are the highest priority (S13: "The menu and ordering pages are the highest priority") |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Customers must be able to add products to a cart and change the quantity of each item [S4: "Customers must be able to add products to a cart and change the quantity of each item"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-008 — Select pickup date and time slot

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-005 |
| Status | Needs clarification (7 open question(s)) |
| Description | Enable customers to choose a pickup date and a pickup time slot when placing an order |
| Source reference | S5: "Customers must choose a pickup date and a pickup time slot when placing an order" |
| Dependencies | None stated in the brief |
| Priority | menu and ordering pages are the highest priority (S13: "The menu and ordering pages are the highest priority") |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Customers must choose a pickup date and a pickup time slot when placing an order [S5: "Customers must choose a pickup date and a pickup time slot when placing an order"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-009 — Generate pickup time slots

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-005 |
| Status | Needs clarification (7 open question(s)) |
| Description | Provide pickup time slots every 30 minutes between 10:00 AM and 8:00 PM |
| Source reference | S6: "Pickup time slots are every 30 minutes between 10:00 AM and 8:00 PM" |
| Dependencies | None stated in the brief |
| Priority | menu and ordering pages are the highest priority (S13: "The menu and ordering pages are the highest priority") |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Pickup time slots are every 30 minutes between 10:00 AM and 8:00 PM [S6: "Pickup time slots are every 30 minutes between 10:00 AM and 8:00 PM"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-010 — Handle cash on pickup payment

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-005 |
| Status | Needs clarification (7 open question(s)) |
| Description | Implement payment as cash on pickup only; no online payment is needed |
| Source reference | S7: "Payment is cash on pickup only; no online payment is needed" |
| Dependencies | None stated in the brief |
| Priority | menu and ordering pages are the highest priority (S13: "The menu and ordering pages are the highest priority") |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- Payment is cash on pickup only; no online payment is needed [S7: "Payment is cash on pickup only; no online payment is needed"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

### TASK-011 — Send order confirmation email

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-005 |
| Status | Needs clarification (7 open question(s)) |
| Description | After placing an order, the customer must receive a confirmation email with an order number |
| Source reference | S8: "After placing an order, the customer must receive a confirmation email with an order number" |
| Dependencies | None stated in the brief |
| Priority | menu and ordering pages are the highest priority (S13: "The menu and ordering pages are the highest priority") |
| Estimate | Not specified |
| Deadline | 15 December 2026 (S14: "The website must go live by 15 December 2026") |

**Acceptance criteria**

- After placing an order, the customer must receive a confirmation email with an order number [S8: "After placing an order, the customer must receive a confirmation email with an order number"]

**Open questions**

- Q-001: What customer contact information is required to place an order and receive the confirmation email?
- Q-002: Do customers need to create an account or log in to place an order, or can they order as guests?
- Q-003: Will staff members need to authenticate to access the admin page, and if so, what authentication method is required?
- Q-004: What is the allowed range of pickup dates that customers can select?
- Q-005: Which email service or provider will be used to send the order confirmation emails?
- Q-006: What does "highest priority" mean in terms of development sequencing and feature completion?
- Q-007: Will customers be able to view the status of their order on the website after placing it?

## Verification (Python checks against the brief)

- Quotes checked: 64
- Issues found: 7
- AI priorities/deadlines/estimates rejected: 0
- Reworded acceptance criteria replaced with the brief's words: 0
- Tickets ready: 0 · needing clarification: 11
- Uncovered features: none
- Brief sentences not used anywhere: none
- Coverage repair needed: True

- ⚠ **not_found** at question Q-001: "After placing an order, the customer must receive a confirmation email with an order number. (S8)" is not in the brief
- ⚠ **not_found** at question Q-002: "The website is for customers who want to order cakes and pastries for pickup. (S2)" is not in the brief
- ⚠ **not_found** at question Q-003: "The bakery staff need an admin page to view all orders for a selected date. (S9)" is not in the brief
- ⚠ **not_found** at question Q-004: "Customers must choose a pickup date and a pickup time slot when placing an order. (S5)" is not in the brief
- ⚠ **not_found** at question Q-005: "After placing an order, the customer must receive a confirmation email with an order number. (S8)" is not in the brief
- ⚠ **not_found** at question Q-006: "The menu and ordering pages are the highest priority. (S13)" is not in the brief
- ⚠ **not_found** at question Q-007: "After placing an order, the customer must receive a confirmation email with an order number. (S8)" is not in the brief
