Run python -m pytest tests/mlops/ -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/DeepPilote/DeepPilote
configfile: pyproject.toml
plugins: anyio-4.14.1, cov-7.1.0
collecting ... collected 30 items

tests/mlops/test_monitoring.py::TestPSI::test_psi_identical_distributions PASSED [  3%]
tests/mlops/test_monitoring.py::TestPSI::test_psi_similar_distributions PASSED [  6%]
tests/mlops/test_monitoring.py::TestPSI::test_psi_different_distributions PASSED [ 10%]
tests/mlops/test_monitoring.py::TestPSI::test_psi_with_nan PASSED        [ 13%]
tests/mlops/test_monitoring.py::TestPSI::test_psi_empty_arrays PASSED    [ 16%]
tests/mlops/test_monitoring.py::TestDataDrift::test_no_drift PASSED      [ 20%]
tests/mlops/test_monitoring.py::TestDataDrift::test_with_drift PASSED    [ 23%]
tests/mlops/test_monitoring.py::TestDataDrift::test_drift_report_structure PASSED [ 26%]
tests/mlops/test_monitoring.py::TestPredictionDrift::test_no_prediction_drift PASSED [ 30%]
tests/mlops/test_monitoring.py::TestPredictionDrift::test_with_prediction_drift PASSED [ 33%]
tests/mlops/test_monitoring.py::TestPerformanceCheck::test_performance_ok PASSED [ 36%]
tests/mlops/test_monitoring.py::TestPerformanceCheck::test_performance_below_threshold PASSED [ 40%]
tests/mlops/test_monitoring.py::TestPerformanceCheck::test_performance_above_max_threshold PASSED [ 43%]
tests/mlops/test_monitoring.py::TestPerformanceCheck::test_missing_metric PASSED [ 46%]
tests/mlops/test_monitoring.py::TestModelMonitor::test_monitor_init PASSED [ 50%]
tests/mlops/test_monitoring.py::TestModelMonitor::test_monitor_check_data PASSED [ 53%]
tests/mlops/test_monitoring.py::TestModelMonitor::test_monitor_check_performance PASSED [ 56%]
tests/mlops/test_monitoring.py::TestModelMonitor::test_monitor_get_status PASSED [ 60%]
tests/mlops/test_tracking.py::TestExperiments::test_get_or_create_experiment_new FAILED [ 63%]
tests/mlops/test_tracking.py::TestExperiments::test_get_or_create_experiment_existing FAILED [ 66%]
tests/mlops/test_tracking.py::TestExperiments::test_get_experiment_id_valid_key FAILED [ 70%]
tests/mlops/test_tracking.py::TestExperiments::test_get_experiment_id_invalid_key FAILED [ 73%]
tests/mlops/test_tracking.py::TestRuns::test_start_run_basic FAILED      [ 76%]
tests/mlops/test_tracking.py::TestRuns::test_start_run_with_tags FAILED  [ 80%]
tests/mlops/test_tracking.py::TestLogging::test_log_params FAILED        [ 83%]
tests/mlops/test_tracking.py::TestLogging::test_log_params_with_list FAILED [ 86%]
tests/mlops/test_tracking.py::TestLogging::test_log_metrics FAILED       [ 90%]
tests/mlops/test_tracking.py::TestLogging::test_log_metrics_with_step FAILED [ 93%]
tests/mlops/test_tracking.py::TestBestRun::test_get_best_run_empty FAILED [ 96%]
tests/mlops/test_tracking.py::TestBestRun::test_get_best_run_with_data FAILED [100%]

=================================== FAILURES ===================================
______________ TestExperiments.test_get_or_create_experiment_new _______________
tests/mlops/test_tracking.py:38: in test_get_or_create_experiment_new
    exp_id = get_or_create_experiment("test_experiment_new")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
____________ TestExperiments.test_get_or_create_experiment_existing ____________
tests/mlops/test_tracking.py:44: in test_get_or_create_experiment_existing
    exp_id1 = get_or_create_experiment("test_experiment_existing")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
_______________ TestExperiments.test_get_experiment_id_valid_key _______________
tests/mlops/test_tracking.py:50: in test_get_experiment_id_valid_key
    exp_id = get_experiment_id("regime_detection")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
______________ TestExperiments.test_get_experiment_id_invalid_key ______________
tests/mlops/test_tracking.py:55: in test_get_experiment_id_invalid_key
    exp_id = get_experiment_id("invalid_key")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
________________________ TestRuns.test_start_run_basic _________________________
tests/mlops/test_tracking.py:64: in test_start_run_basic
    with start_run(experiment="regime_detection", run_name="test_run") as run:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
______________________ TestRuns.test_start_run_with_tags _______________________
tests/mlops/test_tracking.py:70: in test_start_run_with_tags
    with start_run(
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
_________________________ TestLogging.test_log_params __________________________
tests/mlops/test_tracking.py:83: in test_log_params
    with start_run(experiment="regime_detection", run_name="test_params"):
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
____________________ TestLogging.test_log_params_with_list _____________________
tests/mlops/test_tracking.py:93: in test_log_params_with_list
    with start_run(experiment="regime_detection", run_name="test_params_list"):
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
_________________________ TestLogging.test_log_metrics _________________________
tests/mlops/test_tracking.py:101: in test_log_metrics
    with start_run(experiment="regime_detection", run_name="test_metrics"):
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
____________________ TestLogging.test_log_metrics_with_step ____________________
tests/mlops/test_tracking.py:111: in test_log_metrics_with_step
    with start_run(experiment="regime_detection", run_name="test_metrics_step"):
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
_____________________ TestBestRun.test_get_best_run_empty ______________________
tests/mlops/test_tracking.py:122: in test_get_best_run_empty
    result = get_best_run("full_pipeline", metric="accuracy")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:302: in get_best_run
    client = MlflowClient()
             ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
___________________ TestBestRun.test_get_best_run_with_data ____________________
tests/mlops/test_tracking.py:130: in test_get_best_run_with_data
    with start_run(experiment="full_pipeline", run_name=f"run_{i}"):
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
mlops/tracking.py:104: in start_run
    experiment_id = get_experiment_id(experiment)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:74: in get_experiment_id
    return get_or_create_experiment(experiment_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
mlops/tracking.py:50: in get_or_create_experiment
    experiment = mlflow.get_experiment_by_name(name)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/fluent.py:2188: in get_experiment_by_name
    return MlflowClient().get_experiment_by_name(name)
           ^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/client.py:248: in __init__
    self._tracking_client = TrackingServiceClient(final_tracking_uri)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:98: in __init__
    self.store
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/client.py:102: in store
    return utils._get_store(self.tracking_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:270: in _get_store
    return _tracking_store_registry.get_store(store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:45: in get_store
    return self._get_store_with_resolved_uri(resolved_store_uri, artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/registry.py:56: in _get_store_with_resolved_uri
    return builder(store_uri=resolved_store_uri, artifact_uri=artifact_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/tracking/_tracking_service/utils.py:184: in _get_file_store
    return FileStore(store_uri, store_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/mlflow/store/tracking/file_store.py:225: in __init__
    raise MlflowException(
E   mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
=========================== short test summary info ============================
FAILED tests/mlops/test_tracking.py::TestExperiments::test_get_or_create_experiment_new - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestExperiments::test_get_or_create_experiment_existing - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestExperiments::test_get_experiment_id_valid_key - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestExperiments::test_get_experiment_id_invalid_key - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestRuns::test_start_run_basic - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestRuns::test_start_run_with_tags - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestLogging::test_log_params - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestLogging::test_log_params_with_list - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestLogging::test_log_metrics - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestLogging::test_log_metrics_with_step - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestBestRun::test_get_best_run_empty - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
FAILED tests/mlops/test_tracking.py::TestBestRun::test_get_best_run_with_data - mlflow.exceptions.MlflowException: The filesystem tracking backend (e.g., './mlruns') is in maintenance mode and will not receive further updates. Please migrate to a database backend (e.g., 'sqlite:///mlflow.db') to access the latest MLflow features. The `mlflow migrate-filestore` tool migrates your existing data losslessly. See https://mlflow.org/docs/latest/self-hosting/migrate-from-file-store for migration guidance. If the filesystem backend is required for your workflow, set `MLFLOW_ALLOW_FILE_STORE=true` to opt out of this exception.
======================== 12 failed, 18 passed in 3.90s =========================
Error: Process completed with exit code 1.