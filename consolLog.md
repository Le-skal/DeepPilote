Connect to your database

Supabase provides multiple methods to connect to your Postgres database, whether you’re working on the frontend, backend, or using serverless functions.

How to connect to your Postgres databases#
How you connect to your database depends on where you're connecting from:

For frontend applications, use the Data API
For Postgres clients, use a connection string
Use the direct connection string for single sessions or Postgres native commands. For example, database GUIs, client applications like pg_dump, migrations, backup-restore, or specifying connections for replication. The direct endpoint is on IPv6, or on IPv4 if the project has the IPv4 add-on.
Use pooler session mode for application traffic from persistent clients on IPv4-only networks,
Use pooler transaction mode for application traffic from temporary clients (for example, serverless or edge functions).
The table below summarizes each mode, its host and port, IP version support per project tier, and what it's best used for:

Mode	Host:Port	Free	Paid	Paid + IPv4 add-on	Best for
Direct connection	db.[project-id].supabase.co:5432	IPv6	IPv6	IPv4	Migrations, pg_dump, long-lived backend
Shared pooler (Supavisor) - session mode	aws-[region].pooler.supabase.com:5432	IPv4	IPv4	IPv4	Persistent backend on IPv4-only networks
Shared pooler (Supavisor) - transaction mode	aws-[region].pooler.supabase.com:6543	IPv4	IPv4	IPv4	Serverless and edge functions
Dedicated pooler (PgBouncer) - transaction mode	db.[project-id].supabase.co:6543	-	IPv6	IPv4	High-performance app traffic on paid tiers
The IPv4 add-on is not dual-stack: enabling it swaps the project's IPv6 (AAAA) DNS record for an IPv4 (A) record, so the project endpoint becomes reachable only over IPv4.

Quickstarts#
Prisma

Drizzle

Postgres.js

pgAdmin

PSQL

DBeaver

Metabase

Beekeeper Studio

Data APIs and client libraries#
The Data APIs allow you to interact with your database using REST or GraphQL requests. You can use these APIs to fetch and insert data from the frontend, as long as you have RLS enabled.

REST
GraphQL
For convenience, you can also use the Supabase client libraries, which wrap the Data APIs with a developer-friendly interface and automatically handle authentication:

JavaScript
Flutter
Swift
Python
C#
Kotlin
Direct connection#
The direct connection string connects directly to your Postgres instance. It is ideal for persistent servers, such as virtual machines (VMs) and long-lasting containers. Examples include AWS EC2 machines, Fly.io VMs, and DigitalOcean Droplets.

Direct connections are on IPv6, or on IPv4 if the project has the IPv4 add-on. If your network is IPv4-only and you don't have the add-on, use pooler session mode instead.

The connection string looks like this:

postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnopqrst.supabase.co:5432/postgres
Get your project's direct connection string from your project dashboard by clicking Connect.

Poolers#
Supabase offers two poolers. The Shared Pooler (Supavisor) is multi-tenant, available on every project, and IPv4-only. The Dedicated Pooler (PgBouncer) is available on paid plans and co-located with your Postgres instance; like the direct connection, it is on IPv6, or on IPv4 if the project has the IPv4 add-on.

Pooler session mode#
The session mode connection string connects to your Postgres instance via the Shared Pooler (Supavisor). This is only recommended as an alternative to a Direct Connection when connecting from an IPv4-only network.

The connection string looks like this:

postgres://postgres.apbkobhfnmcqqzqeeqss:[YOUR-PASSWORD]@aws-[REGION].pooler.supabase.com:5432/postgres
Get your project's Session pooler connection string from your project dashboard by clicking Connect.

Pooler transaction mode#
The transaction mode connection string connects to your Postgres instance via the Shared Pooler (Supavisor) in transaction-pooling mode. This is ideal for serverless or edge functions, which require many transient connections.

Transaction mode does not support prepared statements. To avoid errors, turn off prepared statements for your connection library.

The connection string looks like this:

postgres://postgres.apbkobhfnmcqqzqeeqss:[YOUR-PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres
Get your project's Transaction pooler connection string from your project dashboard by clicking Connect.

Dedicated pooler#
For paying customers, we provision a Dedicated Pooler (PgBouncer) that's co-located with your Postgres database. The Dedicated Pooler runs in transaction mode only - for session mode, use the Shared Pooler. It is reachable over IPv6, or over IPv4 if the project has the IPv4 add-on.

The connection string looks like this:

postgres://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnopqrst.supabase.co:6543/postgres
The Dedicated Pooler ensures best performance and latency, while using up more of your project's compute resources. If your network supports IPv6 or you have the IPv4 add-on, we encourage you to use the Dedicated Pooler over the Shared Pooler.

Get your project's Dedicated pooler connection string from your project dashboard by clicking Connect.

More about connection pooling#
Connection pooling improves database performance by reusing existing connections between queries. This reduces the overhead of establishing connections and improves scalability.

You can use an application-side pooler or a server-side pooler (Supabase automatically provides one called Supavisor), depending on whether your backend is persistent or serverless.

Application-side poolers#
Application-side poolers are built into connection libraries and API servers, such as Prisma, SQLAlchemy, and PostgREST. They maintain several active connections with Postgres or a server-side pooler, reducing the overhead of establishing connections between queries. When deploying to static architecture, such as long-standing containers or VMs, application-side poolers are satisfactory on their own.

Server-side poolers#
Postgres connections are like a WebSocket. Once established, they are preserved until the client (application server) disconnects. A server might only make a single 10 ms query, but needlessly reserve its database connection for seconds or longer.

Server-side poolers, such as Supabase's Supavisor in transaction mode, sit between clients and the database and can be thought of as load balancers for Postgres connections.