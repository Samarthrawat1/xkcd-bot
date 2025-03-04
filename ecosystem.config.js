module.exports = {
  apps: [{
    name: 'xkcd-bot',
    script: 'xkcd_bot.py',
    interpreter: '/home/sam/xkcd-bot/.venv/bin/python3',
    interpreter_args: '-u',
    autorestart: true,
    watch: false,
    max_memory_restart: '200M',
    error_file: 'logs/error.log',
    out_file: 'logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    exp_backoff_restart_delay: 100,
    cron_restart: '0 0 * * *',
    combine_logs: true,
    restart_delay: 4000,
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: '1',
      PYTHONPATH: '/home/sam/xkcd-bot/.venv/lib/python3.x/site-packages'
    }
  }]
}; 