-- CreateTable
CREATE TABLE "ElicitationResponse" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "respondentCode" TEXT NOT NULL,
    "yearsExperience" INTEGER,
    "institution" TEXT,
    "role" TEXT,
    "level" TEXT NOT NULL,
    "best" TEXT NOT NULL,
    "worst" TEXT NOT NULL,
    "bestToOthers" TEXT NOT NULL,
    "othersToWorst" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE INDEX "ElicitationResponse_level_idx" ON "ElicitationResponse"("level");

-- CreateIndex
CREATE UNIQUE INDEX "ElicitationResponse_respondentCode_level_key" ON "ElicitationResponse"("respondentCode", "level");
