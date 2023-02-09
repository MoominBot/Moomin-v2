-- CreateTable
CREATE TABLE IF NOT EXISTS "Guild" (
    "id" TEXT NOT NULL,
    "blocked" BOOLEAN NOT NULL DEFAULT false,
    "ronb" TEXT,
    "modlog" TEXT
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "ModLogCase" (
    "id" SERIAL NOT NULL,
    "guild" TEXT NOT NULL,
    "case_id" SERIAL NOT NULL,
    "moderator" TEXT NOT NULL,
    "target" TEXT NOT NULL,
    "reason" TEXT NOT NULL DEFAULT E'N/A',
    "type" INTEGER NOT NULL,
    "timestamp" TEXT NOT NULL,
    "message" TEXT,
    "channel" TEXT,

    CONSTRAINT "ModLogCase_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "Guild_id_key" ON "Guild"("id");
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- Create Errors Table
CREATE TABLE IF NOT EXISTS errors (
  error_id UUID DEFAULT uuid_generate_v4(),
  message TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
