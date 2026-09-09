-- CreateTable
CREATE TABLE "LoginAttempt" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "subject" TEXT NOT NULL,
    "clientHash" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE INDEX "LoginAttempt_subject_createdAt_idx" ON "LoginAttempt"("subject", "createdAt");

-- CreateIndex
CREATE INDEX "LoginAttempt_clientHash_createdAt_idx" ON "LoginAttempt"("clientHash", "createdAt");
