output "cosmos_db_uri" {
  value = azurerm_cosmosdb_account.cosmos.endpoint
}

output "blob_storage_url" {
  value = azurerm_storage_container.cold.id
}

output "function_app_url" {
  value = azurerm_linux_function_app.func.default_hostname
}
