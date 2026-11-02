#!/usr/bin/env ruby
# CocoaPods supplies the xcodeproj gem; change only application/extension targets.
require 'json'
require 'xcodeproj'

project = Xcodeproj::Project.open('ios/App/App.xcodeproj')
profiles = JSON.parse(File.read(ARGV.fetch(0)))
expected = profiles.keys.sort
configured = []
project.targets.each do |target|
  next unless %w[com.apple.product-type.application com.apple.product-type.app-extension].include?(target.product_type)

  target.build_configurations.each do |config|
    bundle = config.build_settings['PRODUCT_BUNDLE_IDENTIFIER']
    profile = profiles.fetch(bundle) { abort 'Missing profile for an application target' }
    config.build_settings['CODE_SIGN_STYLE'] = 'Manual'
    config.build_settings['CODE_SIGN_IDENTITY'] = 'Apple Distribution'
    config.build_settings['DEVELOPMENT_TEAM'] = ENV.fetch('APPLE_TEAM_ID')
    config.build_settings['PROVISIONING_PROFILE_SPECIFIER'] = profile
    configured << bundle
  end
end
abort 'Signing profile map does not match application and extension targets' unless configured.uniq.sort == expected
project.save
