#!/usr/bin/env ruby
require "yaml"

root = File.expand_path("..", __dir__)
contract = YAML.load_file(File.join(root, "tests/release.yml"))
errors = []
source_path = contract.fetch("source_path")
source_root = File.join(root, source_path)

files = Dir.glob(File.join(source_root, "**/*"), File::FNM_DOTMATCH).select { |path| File.file?(path) }
relative = files.map { |path| path.delete_prefix("#{source_root}/") }.sort
errors << "source file count #{relative.length}" unless relative.length == contract.fetch("source_file_count")

required = %w[README.md QUICKSTART.md WALKTHROUGH.md SECURITY.md AGENTS.md .env.example .gitignore .dockerignore Dockerfile compose.yaml pyproject.toml alembic.ini app/main.py app/models.py app/database.py app/seed.py tests/test_app.py tests/test_validation.py]
required.each { |path| errors << "missing source/#{path}" unless relative.include?(path) }

prohibited = relative.select do |path|
  path == ".env" || path.start_with?(".git/") || path.match?(%r{(^|/)(__pycache__|\.pytest_cache|node_modules|dist|build|data|volumes?)(/|$)}) || path.match?(/\.(?:pyc|sqlite3?|db|log|pem|key|p12|pfx)$/)
end
prohibited.each { |path| errors << "prohibited source artifact #{path}" }

treeish = ENV.fetch("VERIFY_TREEISH", ENV.fetch("GITHUB_SHA", "HEAD"))
actual_tree = `git -C "#{root}" rev-parse "#{treeish}:#{source_path}" 2>/dev/null`.strip
errors << "source tree differs: #{actual_tree}" unless actual_tree == contract.fetch("source_tree_oid")

version = contract.fetch("repository_version")
%w[README.md SECURITY.md PROVENANCE.md docs/AUTHENTICATION-PROGRESSION.md docs/COMPANION-LINKS.md].each do |path|
  source = File.read(File.join(root, path))
  errors << "#{path}: version mismatch" unless source.match?(/^Version: #{Regexp.escape(version)}$/)
end

readme = File.read(File.join(root, "README.md"))
commands = ["git clone https://github.com/SetonHill/SCS323-Address-Book-Learning-App.git", "git switch --detach v1.0.0", "git switch -c lab/address-book-practice", "cp .env.example .env", "docker compose config --quiet", "docker compose build", "docker compose up -d", "docker compose exec app alembic upgrade head", "docker compose exec app python -m app.seed", "docker compose exec app pytest", "http://127.0.0.1:8000", "docker compose down"]
commands.each { |command| errors << "README missing #{command}" unless readme.include?(command) }

auth = File.read(File.join(root, "docs/AUTHENTICATION-PROGRESSION.md"))
%w[Registration hashing Login logout session Protected ownership migration Authorization production-secret].each do |term|
  errors << "authentication progression missing #{term}" unless auth.downcase.include?(term.downcase)
end
errors << "authentication progression must keep solution off default" unless auth.include?("must not replace `main`")

tracked = `git -C "#{root}" ls-files`.lines.map(&:strip)
tracked.each do |path|
  if path == ".env" || path.match?(%r{(^|/)(id_(rsa|ed25519)|.+\.(pem|key|p12|pfx))$})
    errors << "prohibited tracked path #{path}"
  end
end

if errors.any?
  warn errors.join("\n")
  exit 1
end

puts "Validated exact 33-file Address Book v1.0.0 source, student workflow, and authentication progression contract."
