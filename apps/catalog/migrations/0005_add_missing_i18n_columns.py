# Repair production DBs where django_migrations was ahead of real columns.
# PostgreSQL-only SQL; SQLite/local already has columns from 0001_initial.

from django.db import migrations


def repair_missing_i18n_columns(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute(
        """
        ALTER TABLE catalog_category
          ADD COLUMN IF NOT EXISTS name_th varchar(100) NOT NULL DEFAULT '';
        ALTER TABLE catalog_category
          ADD COLUMN IF NOT EXISTS name_en varchar(100) NOT NULL DEFAULT '';
        ALTER TABLE catalog_category
          ADD COLUMN IF NOT EXISTS slug varchar(120) NULL;

        UPDATE catalog_category
           SET slug = 'cat-' || id::text
         WHERE slug IS NULL OR slug = '';

        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'catalog_category_slug_key'
          ) THEN
            ALTER TABLE catalog_category ADD CONSTRAINT catalog_category_slug_key UNIQUE (slug);
          END IF;
        END $$;

        ALTER TABLE catalog_product
          ADD COLUMN IF NOT EXISTS name_th varchar(200) NOT NULL DEFAULT '';
        ALTER TABLE catalog_product
          ADD COLUMN IF NOT EXISTS name_en varchar(200) NOT NULL DEFAULT '';
        ALTER TABLE catalog_product
          ADD COLUMN IF NOT EXISTS slug varchar(220) NULL;
        ALTER TABLE catalog_product
          ADD COLUMN IF NOT EXISTS description_th text NOT NULL DEFAULT '';
        ALTER TABLE catalog_product
          ADD COLUMN IF NOT EXISTS description_en text NOT NULL DEFAULT '';

        UPDATE catalog_product
           SET slug = 'product-' || id::text
         WHERE slug IS NULL OR slug = '';

        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'catalog_product_slug_key'
          ) THEN
            ALTER TABLE catalog_product ADD CONSTRAINT catalog_product_slug_key UNIQUE (slug);
          END IF;
        END $$;
        """
    )


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_alter_category_name_alter_product_category_and_more"),
    ]

    operations = [
        migrations.RunPython(repair_missing_i18n_columns, migrations.RunPython.noop),
    ]
