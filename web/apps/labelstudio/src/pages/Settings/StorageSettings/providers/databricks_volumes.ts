import { z } from "zod";
import type { ProviderConfig } from "@humansignal/app-common/blocks/StorageProviderForm/types/provider";
import { IconCloudProviderDatabricks } from "@humansignal/icons";

export const databricksVolumesProvider: ProviderConfig = {
  name: "databricks_volumes",
  title: "Databricks Unity Catalog Volumes",
  description: "Configure your Databricks Unity Catalog Volumes connection with all required settings",
  icon: IconCloudProviderDatabricks,
  fields: [
    {
      name: "databricks_host",
      type: "text",
      label: "Databricks Host",
      required: true,
      placeholder: "https://dbc-xxx.cloud.databricks.com",
      schema: z.string().min(1, "Databricks Host is required"),
    },
    {
      name: "catalog",
      type: "text",
      label: "Catalog",
      required: true,
      schema: z.string().min(1, "Catalog is required"),
    },
    {
      name: "schema_name",
      type: "text",
      label: "Schema",
      required: true,
      schema: z.string().min(1, "Schema is required"),
    },
    {
      name: "volume",
      type: "text",
      label: "Volume Name",
      required: true,
      schema: z.string().min(1, "Volume Name is required"),
    },
    {
      name: "prefix",
      type: "text",
      label: "Prefix",
      placeholder: "path/to/files",
      schema: z.string().optional().default(""),
    },
    {
      name: "databricks_client_id",
      type: "password",
      label: "Client ID",
      required: true,
      autoComplete: "new-password",
      accessKey: true,
      schema: z.string().min(1, "Client ID is required"),
    },
    {
      name: "databricks_client_secret",
      type: "password",
      label: "Client Secret",
      required: true,
      autoComplete: "new-password",
      accessKey: true,
      schema: z.string().min(1, "Client Secret is required"),
    },
    {
      name: "regex_filter",
      type: "text",
      label: "File Filter Regex",
      placeholder: ".*csv or .*(jpe?g|png|tiff) or .\\w+-\\d+.text",
      schema: z.string().optional().default(""),
      target: "import",
    },
    {
      name: "use_blob_urls",
      type: "select",
      label: "Import Method",
      description: "Choose how to import your data from storage",
      options: [
        { value: true, label: "Files - Automatically creates a task for each storage object" },
        { value: false, label: "Tasks - Treat each JSON or JSONL file as a task definition" },
      ],
      schema: z.boolean().default(false),
      target: "import",
    },
    {
      name: "recursive_scan",
      type: "toggle",
      label: "Recursive scan",
      description: "Scan nested directories within the volume",
      schema: z.boolean().default(false),
      target: "import",
      resetConnection: false,
    },
  ],
  layout: [
    { fields: ["databricks_host"] },
    { fields: ["catalog", "schema_name"] },
    { fields: ["volume", "prefix"] },
    { fields: ["databricks_client_id", "databricks_client_secret"] },
    { fields: ["regex_filter"] },
    { fields: ["use_blob_urls"] },
    { fields: ["recursive_scan"] },
  ],
};

export default databricksVolumesProvider;
