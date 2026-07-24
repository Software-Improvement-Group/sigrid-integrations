import Commands.download_objectives
import Commands.download_maintainability_json
import Commands.export_architecture_jsons
import Commands.export_portfolio_metadata
import Commands.export_portfolio_security_results
import Commands.export_portfolio_users
import Commands.import_portfolio_metadata
import Commands.onboard_mendix_systems
import Commands.update_portfolio_users
import Commands.generate_mendix_onboarding_template

clis = [Commands.download_objectives.download_objectives,
        Commands.download_maintainability_json.download_maintainability_json,
        Commands.export_architecture_jsons.export_architecture_jsons,
        Commands.export_portfolio_metadata.export_portfolio_metadata,
        Commands.export_portfolio_security_results.export_security_results,
        Commands.export_portfolio_users.export_portfolio_users,
        Commands.import_portfolio_metadata.import_portfolio_metadata,
        Commands.onboard_mendix_systems.onboard_mendix_systems,
        Commands.update_portfolio_users.update_portfolio_users,
        Commands.generate_mendix_onboarding_template.generate_mendix_onboarding_template]

