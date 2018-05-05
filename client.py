  # import local.config
  # parser.add_argument(
  #   "--config", type=str, help="configuration",
  #   default=os.environ.get("CONFIG_STORE")
  # )
  # self.config  = local.config.Storable(
  #   "/opt/baseAdmin/config.json" if args.config  is None else args.config
  # )


if __name__ == "__main__":
  import backend.client
  backend.client.Service("DemoClient").run()
