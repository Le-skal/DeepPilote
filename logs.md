==> Exited with status 1
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
2026/07/09 17:35:44 INFO mlflow.store.db.utils: Creating initial MLflow database tables...
2026/07/09 17:35:45 INFO mlflow.store.db.utils: Updating database tables
2026/07/09 17:35:45 ERROR mlflow.cli: Error initializing backend store
2026/07/09 17:35:45 ERROR mlflow.cli: (psycopg2.OperationalError) connection to server at "aws-0-eu-west-1.pooler.supabase.com" (108.128.216.176), port 5432 failed: FATAL:  (EMAXCONNSESSION) max clients reached in session mode - max clients are limited to pool_size: 15
(Background on this error at: https://sqlalche.me/e/20/e3q8)
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 144, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3319, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 448, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1272, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 712, in checkout
    rec = pool._do_get()
          ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/impl.py", line 178, in _do_get
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 122, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/impl.py", line 176, in _do_get
    return self._create_connection()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 389, in _create_connection
    return _ConnectionRecord(self)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 674, in __init__
    self.__connect()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 900, in __connect
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 122, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 896, in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/create.py", line 667, in connect
    return dialect.connect(*cargs_tup, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 630, in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)  # type: ignore[no-any-return]  # NOQA: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/psycopg2/__init__.py", line 122, in connect
    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
psycopg2.OperationalError: connection to server at "aws-0-eu-west-1.pooler.supabase.com" (108.128.216.176), port 5432 failed: FATAL:  (EMAXCONNSESSION) max clients reached in session mode - max clients are limited to pool_size: 15
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/mlflow/cli.py", line 425, in server
    initialize_backend_stores(backend_store_uri, registry_store_uri, default_artifact_root)
  File "/usr/local/lib/python3.11/site-packages/mlflow/server/handlers.py", line 351, in initialize_backend_stores
    _get_tracking_store(backend_store_uri, default_artifact_root)
  File "/usr/local/lib/python3.11/site-packages/mlflow/server/handlers.py", line 328, in _get_tracking_store
    _tracking_store = _tracking_store_registry.get_store(store_uri, artifact_root)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py", line 42, in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py", line 52, in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/mlflow/server/handlers.py", line 149, in _get_sqlalchemy_store
    return SqlAlchemyStore(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/mlflow/store/tracking/sqlalchemy_store.py", line 170, in __init__
    mlflow.store.db.utils._initialize_tables(self.engine)
  File "/usr/local/lib/python3.11/site-packages/mlflow/store/db/utils.py", line 98, in _initialize_tables
    _upgrade_db(engine)
  File "/usr/local/lib/python3.11/site-packages/mlflow/store/db/utils.py", line 223, in _upgrade_db
    command.upgrade(config, "heads")
  File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 490, in upgrade
    script.run_env()
  File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 556, in run_env
    util.load_python_file(self.dir, "env.py")
  File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
    module = load_module_py(module_id, path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
    spec.loader.exec_module(module)  # type: ignore
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/usr/local/lib/python3.11/site-packages/mlflow/store/db_migrations/env.py", line 86, in <module>
    run_migrations_online()
  File "/usr/local/lib/python3.11/site-packages/mlflow/store/db_migrations/env.py", line 74, in run_migrations_online
    with engine.connect() as connection:
         ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3295, in connect
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 146, in __init__
    Connection._handle_dbapi_exception_noconnection(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2450, in _handle_dbapi_exception_noconnection
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 144, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3319, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 448, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1272, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 712, in checkout
    rec = pool._do_get()
          ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/impl.py", line 178, in _do_get
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 122, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/impl.py", line 176, in _do_get
    return self._create_connection()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 389, in _create_connection
    return _ConnectionRecord(self)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 674, in __init__
    self.__connect()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 900, in __connect
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 122, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 896, in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/create.py", line 667, in connect
    return dialect.connect(*cargs_tup, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 630, in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)  # type: ignore[no-any-return]  # NOQA: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/psycopg2/__init__.py", line 122, in connect
    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "aws-0-eu-west-1.pooler.supabase.com" (108.128.216.176), port 5432 failed: FATAL:  (EMAXCONNSESSION) max clients reached in session mode - max clients are limited to pool_size: 15
(Background on this error at: https://sqlalche.me/e/20/e3q8)