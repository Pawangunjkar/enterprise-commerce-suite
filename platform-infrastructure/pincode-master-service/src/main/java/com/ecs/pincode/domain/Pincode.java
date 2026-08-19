package com.ecs.pincode.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "pincode_master")
public class Pincode extends BaseEntity {

    @Column(nullable = false, unique = true, length = 6)
    private String pincode;

    @Column(nullable = false, length = 80)
    private String city;

    @Column(nullable = false, length = 80)
    private String district;

    @Column(nullable = false, length = 80)
    private String stateName;

    @Column(nullable = false, length = 2)
    private String stateCode;

    @Column(nullable = false)
    private boolean oda;

    @Column(nullable = false)
    private boolean serviceable = true;

    @Column(nullable = false)
    private int standardTransitDays = 4;

    public String getPincode() { return pincode; }
    public void setPincode(String pincode) { this.pincode = pincode; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }
    public String getStateName() { return stateName; }
    public void setStateName(String stateName) { this.stateName = stateName; }
    public String getStateCode() { return stateCode; }
    public void setStateCode(String stateCode) { this.stateCode = stateCode; }
    public boolean isOda() { return oda; }
    public void setOda(boolean oda) { this.oda = oda; }
    public boolean isServiceable() { return serviceable; }
    public void setServiceable(boolean serviceable) { this.serviceable = serviceable; }
    public int getStandardTransitDays() { return standardTransitDays; }
    public void setStandardTransitDays(int standardTransitDays) { this.standardTransitDays = standardTransitDays; }
}
