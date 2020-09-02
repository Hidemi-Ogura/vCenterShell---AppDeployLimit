from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
from cloudshell.workflow.orchestration.sandbox import Sandbox
from AppDeploymentException import AppLimitDeploymentError

sandbox = Sandbox()
api = sandbox.automation_api
res_id = sandbox.id

DefaultSetupWorkflow().register(sandbox)

try:
    sandbox.execute_setup()
except Exception as e:
    err_msg = "App Limit Deployment Error thrown during setup: {}".format(str(e))
    api.WriteMessageToReservationOutput(res_id, err_msg)
    api.SetReservationLiveStatus(reservationId=res_id, liveStatusName="Error", additionalInfo=err_msg)
    api.WriteMessageToReservationOutput(res_id, "=== ENDING RESERVATION ===")
    api.EndReservation(res_id)
