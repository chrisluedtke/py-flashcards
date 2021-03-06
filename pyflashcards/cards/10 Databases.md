##### Question
What are **vertical** and **horizontal** scaling?

##### Answer
* Vertical - upgrading to a more powerful single machine
* Horizontal - acquiring more distributed systems

---

##### Question
What does **ACID** stand for, in the context of relational databases?

##### Answer
4 properties guaranteed by (relational) databases, by keeping a log of everything that happens, they can roll back anything that happens.

* **A**tomicity - each 'transaction' treated as a single "unit" that either succeeds completely or fails completely
* **C**onsistency - transactions must maintain a valid state of the database, as defined by various rules (follow a schema design)
* **I**solation - transactions may occur concurrently. Transactions are isolated from one another, checked for conflict, and performed in an order that may be executed successfully. 
* **D**urability - once a transaction has been committed, it will remain committed even in the event of system failure

---

##### Question
What is **ETL**?

##### Answer
* **E**xtract
* **T**ranform
* **L**oad

---

##### Question
What is **database normalization**?

##### Answer
Branching out text-like data, such that entries are stored once and referred to in other tables by ID (foreign key). This saves space but requires more JOINs in queries, and more complicated queries in general. Normalization can also make frequent large batch updates to the database run slowly, as the normalization requires more primary keys, which must be indexed.

---

##### Question
What is **MapReduce**?

##### Answer


---

##### Question
What is **CAP**, in the context of non-relational databases?

##### Answer
Any 2 of the following 3 are guaranteed by a non-relational database:

* **C**onsistency - every read receives the most recent write or an error
* **A**vailability - every request receives a (non-error) response - without the guarantee that is contains the most recent write
* **P**artition Tolerance - the system continues to operate despite an arbitrary number of messages being dropped (or delayed) by the network between nodes
