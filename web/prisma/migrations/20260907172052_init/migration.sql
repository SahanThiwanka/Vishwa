-- CreateTable
CREATE TABLE "Appraisal" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "reference" TEXT NOT NULL,
    "branch" TEXT NOT NULL,
    "region" TEXT,
    "district" TEXT,
    "facilityAmount" REAL NOT NULL,
    "facilityType" TEXT NOT NULL,
    "productProject" TEXT,
    "projectType" TEXT,
    "businessName" TEXT NOT NULL,
    "registrationNo" TEXT,
    "businessStarted" DATETIME,
    "organisationType" TEXT,
    "address" TEXT,
    "appraisalOfficer" TEXT NOT NULL,
    "dateApplied" DATETIME,
    "dateVisited" DATETIME,
    "inputs" TEXT NOT NULL,
    "result" TEXT,
    "modelVersion" TEXT,
    "creditRiskScore" REAL,
    "developmentScore" REAL,
    "riskBand" TEXT,
    "completeness" REAL,
    "status" TEXT NOT NULL DEFAULT 'DRAFT',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "AuditEvent" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "appraisalId" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "actor" TEXT NOT NULL,
    "role" TEXT,
    "note" TEXT,
    "scoreSnapshot" REAL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "AuditEvent_appraisalId_fkey" FOREIGN KEY ("appraisalId") REFERENCES "Appraisal" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "Appraisal_reference_key" ON "Appraisal"("reference");

-- CreateIndex
CREATE INDEX "Appraisal_status_idx" ON "Appraisal"("status");

-- CreateIndex
CREATE INDEX "Appraisal_createdAt_idx" ON "Appraisal"("createdAt");

-- CreateIndex
CREATE INDEX "AuditEvent_appraisalId_createdAt_idx" ON "AuditEvent"("appraisalId", "createdAt");
