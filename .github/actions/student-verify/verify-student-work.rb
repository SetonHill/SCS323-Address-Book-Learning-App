#!/usr/bin/env ruby

root = ENV.fetch("GITHUB_WORKSPACE")
source_root = File.join(root, "source")
errors = []

required = %w[
  .env.example
  .gitignore
  .dockerignore
  Dockerfile
  compose.yaml
  pyproject.toml
  alembic.ini
  app/main.py
  app/models.py
  app/database.py
  app/seed.py
  tests/test_app.py
  tests/test_validation.py
]

required.each do |path|
  errors << "missing source/#{path}" unless File.file?(File.join(source_root, path))
end

tracked = `git -C "#{root}" ls-files`.lines.map(&:strip)
prohibited = tracked.select do |path|
  path == ".env" ||
    path.end_with?("/.env") ||
    path.match?(%r{(^|/)(__pycache__|\.pytest_cache|node_modules|dist|build|data|volumes?)(/|$)}) ||
    path.match?(%r{(^|/)(id_(rsa|ed25519)|.+\.(?:pyc|sqlite3?|db|log|pem|key|p12|pfx))$})
end
prohibited.each { |path| errors << "prohibited tracked artifact #{path}" }

diff_check = `git -C "#{root}" diff --check HEAD^ HEAD 2>&1`
errors << diff_check.strip unless $?.success?

unless File.read(File.join(source_root, "pyproject.toml")).include?("pytest")
  errors << "source/pyproject.toml must retain the test dependency"
end

if errors.any?
  warn errors.reject(&:empty?).join("\n")
  exit 1
end

puts "Repository structure and tracked-artifact safety checks passed."
