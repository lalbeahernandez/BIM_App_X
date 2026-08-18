CREATE TABLE IF NOT EXISTS organizations (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS projects (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES organizations(id),
  code text NOT NULL,
  name text NOT NULL,
  timezone text NOT NULL DEFAULT 'UTC',
  currency char(3) NOT NULL DEFAULT 'EUR',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, code)
);

CREATE TABLE IF NOT EXISTS models (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  discipline text,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_revisions (
  id uuid PRIMARY KEY,
  model_id uuid NOT NULL REFERENCES models(id) ON DELETE CASCADE,
  revision_no integer NOT NULL,
  file_name text NOT NULL,
  file_sha256 text,
  ifc_schema text,
  status text NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED','PROCESSING','READY','FAILED')),
  artifact_uri text,
  error_message text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (model_id, revision_no)
);

CREATE TABLE IF NOT EXISTS bim_elements (
  id uuid PRIMARY KEY,
  revision_id uuid NOT NULL REFERENCES model_revisions(id) ON DELETE CASCADE,
  global_id text NOT NULL,
  ifc_class text NOT NULL,
  name text,
  storey text,
  object_type text,
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  bbox geometry(PolygonZ, 0),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (revision_id, global_id)
);
CREATE INDEX IF NOT EXISTS ix_bim_elements_revision_class ON bim_elements(revision_id, ifc_class);
CREATE INDEX IF NOT EXISTS ix_bim_elements_global_id ON bim_elements(global_id);
CREATE INDEX IF NOT EXISTS ix_bim_elements_properties_gin ON bim_elements USING gin(properties);

CREATE TABLE IF NOT EXISTS element_lineage (
  id uuid PRIMARY KEY,
  from_element_id uuid NOT NULL REFERENCES bim_elements(id) ON DELETE CASCADE,
  to_element_id uuid NOT NULL REFERENCES bim_elements(id) ON DELETE CASCADE,
  match_method text NOT NULL,
  confidence numeric(5,4),
  approved_by text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (from_element_id, to_element_id)
);

CREATE TABLE IF NOT EXISTS classification_nodes (
  id uuid PRIMARY KEY,
  project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
  system text NOT NULL,
  code text NOT NULL,
  label text NOT NULL,
  parent_id uuid REFERENCES classification_nodes(id),
  uri text,
  UNIQUE (project_id, system, code)
);

CREATE TABLE IF NOT EXISTS element_classifications (
  element_id uuid NOT NULL REFERENCES bim_elements(id) ON DELETE CASCADE,
  classification_id uuid NOT NULL REFERENCES classification_nodes(id) ON DELETE CASCADE,
  source text NOT NULL DEFAULT 'manual',
  confidence numeric(5,4),
  PRIMARY KEY (element_id, classification_id)
);

CREATE TABLE IF NOT EXISTS quantities (
  id uuid PRIMARY KEY,
  element_id uuid REFERENCES bim_elements(id) ON DELETE CASCADE,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name text NOT NULL,
  value numeric(24,8) NOT NULL,
  unit text NOT NULL,
  source text NOT NULL,
  rule_id text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS boq_items (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  parent_id uuid REFERENCES boq_items(id),
  code text NOT NULL,
  description text NOT NULL,
  unit text NOT NULL,
  quantity numeric(24,8) NOT NULL DEFAULT 0,
  rate numeric(24,8) NOT NULL DEFAULT 0,
  currency char(3) NOT NULL DEFAULT 'EUR',
  revision integer NOT NULL DEFAULT 1,
  status text NOT NULL DEFAULT 'DRAFT',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (project_id, code, revision)
);

CREATE TABLE IF NOT EXISTS element_boq_links (
  element_id uuid NOT NULL REFERENCES bim_elements(id) ON DELETE CASCADE,
  boq_item_id uuid NOT NULL REFERENCES boq_items(id) ON DELETE CASCADE,
  source text NOT NULL DEFAULT 'manual',
  rule_id text,
  weight numeric(12,8) NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (element_id, boq_item_id)
);

CREATE TABLE IF NOT EXISTS wbs_nodes (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  parent_id uuid REFERENCES wbs_nodes(id),
  code text NOT NULL,
  name text NOT NULL,
  UNIQUE(project_id, code)
);

CREATE TABLE IF NOT EXISTS activities (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  wbs_id uuid REFERENCES wbs_nodes(id),
  external_id text,
  name text NOT NULL,
  planned_start date,
  planned_finish date,
  actual_start date,
  actual_finish date,
  duration_minutes integer,
  percent_complete numeric(7,4) NOT NULL DEFAULT 0,
  calendar_id uuid,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS activity_relations (
  predecessor_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
  successor_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
  relation_type text NOT NULL CHECK (relation_type IN ('FS','SS','FF','SF')),
  lag_minutes integer NOT NULL DEFAULT 0,
  PRIMARY KEY (predecessor_id, successor_id, relation_type)
);

CREATE TABLE IF NOT EXISTS element_activity_links (
  element_id uuid NOT NULL REFERENCES bim_elements(id) ON DELETE CASCADE,
  activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
  role text NOT NULL DEFAULT 'construct',
  source text NOT NULL DEFAULT 'manual',
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (element_id, activity_id, role)
);

CREATE TABLE IF NOT EXISTS resources (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  resource_type text NOT NULL,
  code text,
  name text NOT NULL,
  unit_cost numeric(24,8),
  currency char(3)
);

CREATE TABLE IF NOT EXISTS crews (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  code text NOT NULL,
  name text NOT NULL,
  UNIQUE(project_id, code)
);

CREATE TABLE IF NOT EXISTS productivity_rates (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  activity_type text NOT NULL,
  quantity_unit text NOT NULL,
  output_per_hour numeric(24,8) NOT NULL,
  crew_id uuid REFERENCES crews(id),
  source text,
  effective_from date
);

CREATE TABLE IF NOT EXISTS progress_records (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  activity_id uuid REFERENCES activities(id) ON DELETE CASCADE,
  element_id uuid REFERENCES bim_elements(id) ON DELETE SET NULL,
  data_date date NOT NULL,
  quantity_complete numeric(24,8),
  quantity_unit text,
  percent_complete numeric(7,4),
  source text NOT NULL,
  evidence_uri text,
  created_by text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_progress_project_date ON progress_records(project_id, data_date);

CREATE TABLE IF NOT EXISTS issues (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title text NOT NULL,
  description text,
  status text NOT NULL DEFAULT 'OPEN',
  priority text NOT NULL DEFAULT 'NORMAL',
  assigned_to text,
  viewpoint jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  closed_at timestamptz
);

CREATE TABLE IF NOT EXISTS issue_elements (
  issue_id uuid NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  element_id uuid NOT NULL REFERENCES bim_elements(id) ON DELETE CASCADE,
  PRIMARY KEY (issue_id, element_id)
);

CREATE TABLE IF NOT EXISTS inspections (
  id uuid PRIMARY KEY,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  activity_id uuid REFERENCES activities(id),
  element_id uuid REFERENCES bim_elements(id),
  checklist_code text,
  status text NOT NULL DEFAULT 'PLANNED',
  result jsonb NOT NULL DEFAULT '{}'::jsonb,
  performed_at timestamptz,
  performed_by text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  project_id uuid,
  actor text,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text NOT NULL,
  before_data jsonb,
  after_data jsonb,
  occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS outbox_events (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  project_id uuid,
  event_type text NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz,
  attempts integer NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_outbox_unpublished ON outbox_events(created_at) WHERE published_at IS NULL;
